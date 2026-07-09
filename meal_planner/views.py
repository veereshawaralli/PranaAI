import json
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import MealPlan
from .forms import MealPlanForm


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
def generate_plan(request):
    """Generate a personalized 7-day meal plan using AI."""
    if request.method == 'POST':
        form = MealPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.user = request.user

            # Build context from user profile and health data
            user = request.user
            user_info = f"Patient: {user.get_full_name() or user.username}"
            if user.date_of_birth:
                user_info += f", DOB: {user.date_of_birth}"
            if user.blood_group:
                user_info += f", Blood Group: {user.blood_group}"

            # Pull recent health metrics if available
            health_context = ""
            try:
                from analytics.models import HealthMetric
                recent = HealthMetric.objects.filter(user=user).order_by('-recorded_at')[:10]
                if recent:
                    health_context = "Recent Health Data:\n"
                    for m in recent:
                        health_context += f"- {m.get_metric_type_display()}: {m.display_value}\n"
            except Exception:
                pass

            calorie_note = ""
            if plan.calorie_target:
                calorie_note = f"Target daily calories: approximately {plan.calorie_target} kcal."

            prompt = f"""You are a nutrition and meal planning AI for the Prana AI health app.
Generate a personalized 7-day meal plan based on these requirements:

{user_info}
Goal: {plan.get_goal_display()}
Dietary Preference: {plan.get_dietary_preference_display()}
Allergies/Restrictions: {plan.allergies or 'None'}
{calorie_note}

{health_context}

IMPORTANT: Respond in the following JSON format ONLY, with no extra text:
{{
    "days": [
        {{
            "day": "Monday",
            "meals": {{
                "breakfast": {{"name": "<meal name>", "description": "<brief description>", "calories": <estimated kcal>}},
                "morning_snack": {{"name": "<meal name>", "description": "<brief description>", "calories": <estimated kcal>}},
                "lunch": {{"name": "<meal name>", "description": "<brief description>", "calories": <estimated kcal>}},
                "evening_snack": {{"name": "<meal name>", "description": "<brief description>", "calories": <estimated kcal>}},
                "dinner": {{"name": "<meal name>", "description": "<brief description>", "calories": <estimated kcal>}}
            }},
            "total_calories": <total for the day>,
            "tip": "<a short health/nutrition tip for the day>"
        }}
    ],
    "notes": "<2-3 sentences of general dietary advice tailored to the user's goal and health data>"
}}

Generate all 7 days (Monday through Sunday). Make meals realistic, varied, and culturally diverse.
Include Indian cuisine where appropriate for vegetarian/eggetarian preferences.
DISCLAIMER: This is for educational purposes only. Consult a nutritionist for professional advice."""

            try:
                import google.generativeai as genai
                from django.conf import settings as django_settings
                from dotenv import load_dotenv
                load_dotenv(os.path.join(django_settings.BASE_DIR, '.env'))

                api_key = os.environ.get('GEMINI_API_KEY')
                if not api_key:
                    messages.error(request, "AI API key not configured.")
                    return redirect('meal_planner:generate_plan')

                api_key = api_key.strip('"').strip("'")
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')

                try:
                    response = model.generate_content(prompt)
                    response_text = response.text.strip()
                except Exception as gemini_err:
                    error_msg = str(gemini_err).lower()
                    if "429" in error_msg or "quota" in error_msg or "rate limit" in error_msg or "exhausted" in error_msg:
                        print("Gemini limit reached. Falling back to Groq for Meal Planner.")
                        response_text = get_groq_fallback_json(prompt).strip()
                    else:
                        raise gemini_err

                # Parse JSON
                if response_text.startswith('```'):
                    lines = response_text.split('\n')
                    response_text = '\n'.join(lines[1:-1])

                result = json.loads(response_text)
                plan.plan_data = result.get('days', [])
                plan.ai_notes = result.get('notes', '')
                plan.save()

                messages.success(request, "Your personalized meal plan is ready!")
                return redirect('meal_planner:view_plan', plan_id=plan.id)

            except json.JSONDecodeError:
                plan.plan_data = []
                plan.ai_notes = "Could not parse AI response. Please try generating again."
                plan.save()
                messages.warning(request, "AI response parsing issue. Please try again.")
                return redirect('meal_planner:view_plan', plan_id=plan.id)
            except Exception as e:
                messages.error(request, f"Failed to generate plan: {str(e)}")
                return redirect('meal_planner:generate_plan')
    else:
        form = MealPlanForm()

    return render(request, 'meal_planner/generate.html', {'form': form})


@login_required
def view_plan(request, plan_id):
    """Display a saved meal plan."""
    plan = get_object_or_404(MealPlan, id=plan_id, user=request.user)
    return render(request, 'meal_planner/view_plan.html', {'plan': plan})


@login_required
def plan_history(request):
    """List of previously generated meal plans."""
    plans = MealPlan.objects.filter(user=request.user)
    return render(request, 'meal_planner/history.html', {'plans': plans})
