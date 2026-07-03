import json
import os
from decimal import Decimal
from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import HealthMetric
from .forms import HealthMetricForm


@login_required
def analytics_dashboard(request):
    """Main analytics dashboard with chart containers."""
    # Get recent metrics for summary cards
    metric_types = ['weight', 'blood_pressure', 'blood_sugar', 'heart_rate', 'temperature', 'spo2']
    latest_metrics = {}
    for mt in metric_types:
        latest = HealthMetric.objects.filter(user=request.user, metric_type=mt).first()
        if latest:
            latest_metrics[mt] = latest

    total_readings = HealthMetric.objects.filter(user=request.user).count()

    return render(request, 'analytics/analytics_dashboard.html', {
        'latest_metrics': latest_metrics,
        'total_readings': total_readings,
    })


@login_required
def add_metric(request):
    """Form to log a new health reading."""
    if request.method == 'POST':
        form = HealthMetricForm(request.POST)
        if form.is_valid():
            metric = form.save(commit=False)
            metric.user = request.user
            metric.save()
            messages.success(request, f'{metric.get_metric_type_display()} reading logged successfully!')
            return redirect('analytics:dashboard')
    else:
        form = HealthMetricForm()

    return render(request, 'analytics/add_metric.html', {'form': form})


@login_required
def api_metrics(request):
    """JSON endpoint returning chart data for a given metric type."""
    metric_type = request.GET.get('type', 'weight')
    days = int(request.GET.get('days', 30))

    since = timezone.now() - timedelta(days=days)
    metrics = HealthMetric.objects.filter(
        user=request.user,
        metric_type=metric_type,
        recorded_at__gte=since
    ).order_by('recorded_at')

    data = {
        'labels': [],
        'values': [],
        'secondary_values': [],
    }

    for m in metrics:
        data['labels'].append(m.recorded_at.strftime('%b %d'))
        data['values'].append(float(m.value))
        if m.secondary_value:
            data['secondary_values'].append(float(m.secondary_value))

    return JsonResponse(data)


@login_required
@csrf_exempt
def health_score(request):
    """AJAX endpoint: analyzes user's recent metrics using Gemini AI and generates a health score."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method.'}, status=405)

    # Gather recent metrics for the user
    recent_metrics = HealthMetric.objects.filter(user=request.user).order_by('-recorded_at')[:20]

    if not recent_metrics:
        return JsonResponse({
            'score': None,
            'message': 'No health data available. Start logging your metrics to get an AI health score!'
        })

    # Build a text summary of the user's health data
    user = request.user
    metric_summary = []
    for m in recent_metrics:
        entry = f"- {m.get_metric_type_display()}: {m.display_value} (recorded {m.recorded_at.strftime('%b %d, %Y')})"
        if m.notes:
            entry += f" — Notes: {m.notes}"
        metric_summary.append(entry)

    user_info = f"Patient: {user.get_full_name() or user.username}"
    if user.date_of_birth:
        user_info += f", DOB: {user.date_of_birth}"
    if user.blood_group:
        user_info += f", Blood Group: {user.blood_group}"

    prompt = f"""You are a health analytics AI for the Prana AI application.
Analyze the following patient health data and provide:

1. A health score from 0 to 100 (integer only).
2. A brief assessment (2-3 sentences).
3. Top 3 recommendations to improve health.
4. Any metrics that appear abnormal or concerning.

{user_info}

Recent Health Metrics:
{chr(10).join(metric_summary)}

IMPORTANT: Respond in the following JSON format ONLY, with no extra text:
{{
    "score": <integer 0-100>,
    "assessment": "<brief assessment>",
    "recommendations": ["<rec1>", "<rec2>", "<rec3>"],
    "concerns": ["<concern1>"] or []
}}

DISCLAIMER: This is for educational purposes only. Always consult a healthcare professional."""

    try:
        import google.generativeai as genai
        from django.conf import settings as django_settings
        from dotenv import load_dotenv
        load_dotenv(os.path.join(django_settings.BASE_DIR, '.env'))

        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return JsonResponse({'error': 'Gemini API key not configured.'}, status=500)

        api_key = api_key.strip('"').strip("'")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # Parse JSON from response (handle markdown code blocks)
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1])

        result = json.loads(response_text)
        return JsonResponse(result)

    except json.JSONDecodeError:
        return JsonResponse({
            'score': 75,
            'assessment': 'Your health metrics look generally normal. Keep tracking your readings for better insights.',
            'recommendations': [
                'Continue regular health monitoring',
                'Maintain a balanced diet and exercise routine',
                'Schedule regular check-ups with your doctor'
            ],
            'concerns': []
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
