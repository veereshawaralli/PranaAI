import json
import os
from datetime import timedelta
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import TruncDate
from .models import FoodScan
from .forms import FoodScanForm
import PIL.Image


def get_groq_vision_fallback(prompt_text, img_path):
    """Fallback to Groq vision model when Gemini quota is exhausted."""
    import base64
    from groq import Groq
    from django.conf import settings
    from dotenv import load_dotenv
    load_dotenv(os.path.join(settings.BASE_DIR, '.env'))
    groq_api_key = os.environ.get('GROQ_API_KEY')
    if not groq_api_key:
        raise ValueError("Groq API key is not configured.")

    with open(img_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')

    client = Groq(api_key=groq_api_key)
    completion = client.chat.completions.create(
        model="llama-3.2-11b-vision-preview",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt_text},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]
        }],
        temperature=0.7,
        max_tokens=1024,
    )
    return completion.choices[0].message.content


def get_gemini_model():
    """Initialize and return Gemini model."""
    import google.generativeai as genai
    from django.conf import settings
    from dotenv import load_dotenv
    load_dotenv(os.path.join(settings.BASE_DIR, '.env'))
    api_key = os.environ.get('GEMINI_API_KEY')
    if api_key:
        api_key = api_key.strip('"').strip("'")
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-2.5-flash')
    return None


@login_required
def scan_food(request):
    """Upload a meal photo for AI analysis."""
    if request.method == 'POST':
        form = FoodScanForm(request.POST, request.FILES)
        if form.is_valid():
            scan = form.save(commit=False)
            scan.user = request.user
            scan.save()
            return redirect('diet_tracker:scan_result', scan_id=scan.id)
    else:
        form = FoodScanForm()

    # Recent scans for quick reference
    recent_scans = FoodScan.objects.filter(user=request.user)[:5]
    return render(request, 'diet_tracker/scan.html', {
        'form': form,
        'recent_scans': recent_scans,
    })


@login_required
def scan_result(request, scan_id):
    """Analyze a food scan with Gemini AI and display results."""
    scan = get_object_or_404(FoodScan, id=scan_id, user=request.user)

    # If already analyzed, just show the result
    if scan.ai_analysis:
        return render(request, 'diet_tracker/result.html', {'scan': scan})

    prompt = """You are a nutrition AI assistant for the Prana AI health app.
Analyze this food image carefully. Identify the food items visible and estimate their nutritional content.

IMPORTANT: Respond in the following JSON format ONLY, with no extra text:
{
    "food_name": "<name of the dish/food items>",
    "calories": <estimated total calories as a number>,
    "protein": <grams of protein as a number>,
    "carbs": <grams of carbohydrates as a number>,
    "fat": <grams of fat as a number>,
    "fiber": <grams of fiber as a number>,
    "analysis": "<A detailed 3-4 sentence nutritional analysis including health benefits, potential concerns, and suggestions for making the meal healthier. Include vitamin/mineral highlights.>"
}

Be as accurate as possible with your estimates based on typical serving sizes visible in the image.
DISCLAIMER: These are AI estimates for educational purposes only."""

    try:
        model = get_gemini_model()
        if not model:
            messages.error(request, "AI API key is missing or invalid.")
            return redirect('diet_tracker:scan_food')

        img_path = scan.image.path
        img = PIL.Image.open(img_path)

        try:
            response = model.generate_content([prompt, img])
            response_text = response.text.strip()
        except Exception as gemini_err:
            error_msg = str(gemini_err).lower()
            if "429" in error_msg or "quota" in error_msg or "rate limit" in error_msg or "exhausted" in error_msg:
                print("Gemini limit reached. Falling back to Groq for Food Scanner.")
                response_text = get_groq_vision_fallback(prompt, img_path).strip()
            else:
                raise gemini_err

        # Parse JSON from response
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1])

        result = json.loads(response_text)

        scan.food_name = result.get('food_name', 'Unknown Food')
        scan.calories = Decimal(str(result.get('calories', 0)))
        scan.protein = Decimal(str(result.get('protein', 0)))
        scan.carbs = Decimal(str(result.get('carbs', 0)))
        scan.fat = Decimal(str(result.get('fat', 0)))
        scan.fiber = Decimal(str(result.get('fiber', 0)))
        scan.ai_analysis = result.get('analysis', '')
        scan.save()

        messages.success(request, f"Analysis complete! Detected: {scan.food_name}")

    except json.JSONDecodeError:
        scan.food_name = "Food Item"
        scan.calories = Decimal('0')
        scan.ai_analysis = "Could not parse AI response. Please try scanning again."
        scan.save()
        messages.warning(request, "AI response could not be fully parsed. Basic results shown.")
    except Exception as e:
        error_msg = str(e)
        messages.error(request, f"Failed to analyze image: {error_msg}")
        return render(request, 'diet_tracker/result.html', {'scan': scan, 'error': error_msg})

    return render(request, 'diet_tracker/result.html', {'scan': scan})


@login_required
def food_history(request):
    """Show food scan history with daily calorie totals."""
    scans = FoodScan.objects.filter(user=request.user)

    # Today's stats
    today = timezone.now().date()
    today_scans = scans.filter(scanned_at__date=today)
    today_calories = today_scans.aggregate(total=Sum('calories'))['total'] or 0
    today_protein = today_scans.aggregate(total=Sum('protein'))['total'] or 0
    today_carbs = today_scans.aggregate(total=Sum('carbs'))['total'] or 0
    today_fat = today_scans.aggregate(total=Sum('fat'))['total'] or 0

    return render(request, 'diet_tracker/history.html', {
        'scans': scans[:30],
        'today_calories': today_calories,
        'today_protein': today_protein,
        'today_carbs': today_carbs,
        'today_fat': today_fat,
        'total_scans': scans.count(),
    })


@login_required
def api_daily_calories(request):
    """JSON endpoint returning daily calorie totals for chart."""
    days = int(request.GET.get('days', 7))
    since = timezone.now() - timedelta(days=days)

    daily = (
        FoodScan.objects.filter(user=request.user, scanned_at__gte=since)
        .annotate(date=TruncDate('scanned_at'))
        .values('date')
        .annotate(total_calories=Sum('calories'))
        .order_by('date')
    )

    data = {
        'labels': [d['date'].strftime('%b %d') for d in daily],
        'values': [float(d['total_calories'] or 0) for d in daily],
    }
    return JsonResponse(data)
