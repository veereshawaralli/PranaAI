import json
import os
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg, Count
from .models import MoodEntry
from .forms import MoodEntryForm


def get_groq_fallback_json(prompt_text):
    """Fallback to Groq when Gemini quota is exhausted."""
    from groq import Groq
    from django.conf import settings
    from dotenv import load_dotenv
    load_dotenv(os.path.join(settings.BASE_DIR, '.env'))
    groq_api_key = os.environ.get('GROQ_API_KEY')
    if not groq_api_key:
        raise ValueError("Groq API key is not configured.")
    client = Groq(api_key=groq_api_key)
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt_text}],
        response_format={"type": "json_object"},
        temperature=0.7,
    )
    return completion.choices[0].message.content


@login_required
def check_in(request):
    """Daily mood check-in form with AI sentiment analysis."""
    today = timezone.now().date()

    # Check if already checked in today
    existing = MoodEntry.objects.filter(user=request.user, entry_date=today).first()
    if existing and request.method == 'GET':
        messages.info(request, "You've already checked in today! Viewing your entry.")
        return redirect('mood_journal:entry_detail', entry_id=existing.id)

    if request.method == 'POST':
        form = MoodEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user

            # If there's already an entry for this date, update it
            existing_entry = MoodEntry.objects.filter(
                user=request.user, entry_date=entry.entry_date
            ).first()
            if existing_entry:
                existing_entry.mood_score = entry.mood_score
                existing_entry.journal_text = entry.journal_text
                existing_entry.activities = entry.activities
                existing_entry.sleep_hours = entry.sleep_hours
                entry = existing_entry

            # AI sentiment analysis
            if entry.journal_text:
                prompt = f"""You are a compassionate mental health AI assistant for the Prana AI health app.
Analyze the following mood journal entry and provide mental health insights.

Mood Score: {entry.mood_score}/5 ({entry.get_mood_score_display()})
Activities: {entry.activities or 'Not specified'}
Sleep: {entry.sleep_hours or 'Not specified'} hours
Journal Entry: "{entry.journal_text}"

IMPORTANT: Respond in the following JSON format ONLY, with no extra text:
{{
    "sentiment": "<positive|neutral|negative>",
    "analysis": "<A warm, empathetic 3-4 sentence analysis of the person's emotional state. Acknowledge their feelings, identify patterns, and offer genuine support.>",
    "suggestions": [
        "<suggestion 1: a specific, actionable mindfulness or self-care exercise>",
        "<suggestion 2: a relevant activity or coping strategy>",
        "<suggestion 3: an encouragement or affirmation>"
    ],
    "concern_level": "<low|moderate|high>",
    "concern_note": "<If concern_level is high, a gentle note encouraging professional support. Otherwise empty string.>"
}}

Be warm, non-judgmental, and supportive. Never diagnose conditions.
DISCLAIMER: This is for educational and self-reflection purposes only. Not a substitute for professional mental health care."""

                try:
                    import google.generativeai as genai
                    from django.conf import settings as django_settings
                    from dotenv import load_dotenv
                    load_dotenv(os.path.join(django_settings.BASE_DIR, '.env'))

                    api_key = os.environ.get('GEMINI_API_KEY')
                    if api_key:
                        api_key = api_key.strip('"').strip("'")
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel('gemini-2.5-flash')

                        try:
                            response = model.generate_content(prompt)
                            response_text = response.text.strip()
                        except Exception as gemini_err:
                            error_msg = str(gemini_err).lower()
                            if "429" in error_msg or "quota" in error_msg or "rate limit" in error_msg or "exhausted" in error_msg:
                                print("Gemini limit reached. Falling back to Groq for Mood Journal.")
                                response_text = get_groq_fallback_json(prompt).strip()
                            else:
                                raise gemini_err

                        if response_text.startswith('```'):
                            lines = response_text.split('\n')
                            response_text = '\n'.join(lines[1:-1])

                        result = json.loads(response_text)
                        entry.ai_sentiment = result.get('sentiment', 'neutral')
                        analysis_parts = [result.get('analysis', '')]
                        suggestions = result.get('suggestions', [])
                        if suggestions:
                            analysis_parts.append('\n\n💡 **Suggestions:**')
                            for i, s in enumerate(suggestions, 1):
                                analysis_parts.append(f'{i}. {s}')
                        concern_note = result.get('concern_note', '')
                        if concern_note:
                            analysis_parts.append(f'\n\n⚠️ {concern_note}')
                        entry.ai_analysis = '\n'.join(analysis_parts)

                except json.JSONDecodeError:
                    entry.ai_sentiment = 'neutral'
                    entry.ai_analysis = 'Thank you for sharing. Keep journaling — it helps build self-awareness.'
                except Exception as e:
                    print(f"Mood AI error: {e}")
                    entry.ai_sentiment = 'neutral'
                    entry.ai_analysis = 'Thank you for checking in today. Your journal has been saved.'

            entry.save()
            messages.success(request, "Mood check-in saved! 🎉")
            return redirect('mood_journal:entry_detail', entry_id=entry.id)
    else:
        form = MoodEntryForm()

    return render(request, 'mood_journal/check_in.html', {'form': form})


@login_required
def journal_dashboard(request):
    """Main mood journal dashboard with trend chart and entries."""
    entries = MoodEntry.objects.filter(user=request.user)

    # Stats
    total_entries = entries.count()
    avg_mood = entries.aggregate(avg=Avg('mood_score'))['avg']

    # Streak calculation
    streak = 0
    today = timezone.now().date()
    check_date = today
    while entries.filter(entry_date=check_date).exists():
        streak += 1
        check_date -= timedelta(days=1)

    # Mood distribution
    mood_counts = {i: entries.filter(mood_score=i).count() for i in range(1, 6)}

    # Recent entries
    recent_entries = entries[:10]

    return render(request, 'mood_journal/dashboard.html', {
        'total_entries': total_entries,
        'avg_mood': avg_mood,
        'streak': streak,
        'mood_counts': mood_counts,
        'recent_entries': recent_entries,
    })


@login_required
def entry_detail(request, entry_id):
    """View a single mood entry with AI analysis."""
    entry = get_object_or_404(MoodEntry, id=entry_id, user=request.user)
    return render(request, 'mood_journal/entry_detail.html', {'entry': entry})


@login_required
def api_mood_data(request):
    """JSON endpoint returning mood scores for chart."""
    days = int(request.GET.get('days', 30))
    since = timezone.now() - timedelta(days=days)

    entries = MoodEntry.objects.filter(
        user=request.user, entry_date__gte=since
    ).order_by('entry_date')

    data = {
        'labels': [e.entry_date.strftime('%b %d') for e in entries],
        'values': [e.mood_score for e in entries],
        'sleep': [float(e.sleep_hours) if e.sleep_hours else None for e in entries],
    }
    return JsonResponse(data)


@login_required
@csrf_exempt
def weekly_insight(request):
    """AJAX endpoint: Gemini analyzes the last 7 entries for patterns."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method.'}, status=405)

    entries = MoodEntry.objects.filter(user=request.user).order_by('-entry_date')[:7]

    if len(entries) < 3:
        return JsonResponse({
            'insight': None,
            'message': 'Log at least 3 mood entries to get weekly insights!'
        })

    entries_summary = []
    for e in entries:
        entry_text = f"- {e.entry_date.strftime('%b %d')}: Mood {e.mood_score}/5 ({e.get_mood_score_display()})"
        if e.activities:
            entry_text += f", Activities: {e.activities}"
        if e.sleep_hours:
            entry_text += f", Sleep: {e.sleep_hours}h"
        if e.journal_text:
            entry_text += f", Journal: \"{e.journal_text[:150]}\""
        entries_summary.append(entry_text)

    prompt = f"""You are a compassionate mental health AI for the Prana AI app.
Analyze these recent mood journal entries and identify patterns:

{chr(10).join(entries_summary)}

IMPORTANT: Respond in the following JSON format ONLY:
{{
    "overall_trend": "<improving|stable|declining>",
    "pattern_summary": "<2-3 sentence summary of emotional patterns observed>",
    "key_insight": "<One key insight about what affects this person's mood most>",
    "recommendation": "<One specific, actionable recommendation for the coming week>",
    "encouragement": "<A warm, personalized encouragement message>"
}}

Be warm, supportive, and non-judgmental. Never diagnose.
DISCLAIMER: For educational/self-reflection purposes only."""

    try:
        import google.generativeai as genai
        from django.conf import settings as django_settings
        from dotenv import load_dotenv
        load_dotenv(os.path.join(django_settings.BASE_DIR, '.env'))

        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return JsonResponse({'error': 'AI API key not configured.'}, status=500)

        api_key = api_key.strip('"').strip("'")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        try:
            response = model.generate_content(prompt)
            response_text = response.text.strip()
        except Exception as gemini_err:
            error_msg = str(gemini_err).lower()
            if "429" in error_msg or "quota" in error_msg or "rate limit" in error_msg or "exhausted" in error_msg:
                response_text = get_groq_fallback_json(prompt).strip()
            else:
                raise gemini_err

        if response_text.startswith('```'):
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1])

        result = json.loads(response_text)
        return JsonResponse(result)

    except json.JSONDecodeError:
        return JsonResponse({
            'overall_trend': 'stable',
            'pattern_summary': 'Your mood has been relatively stable. Keep tracking to get deeper insights.',
            'key_insight': 'Regular journaling itself is a positive practice for mental health.',
            'recommendation': 'Try adding a brief mindfulness or breathing exercise to your daily routine.',
            'encouragement': 'You\'re doing great by showing up and checking in with yourself! 🌟'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
