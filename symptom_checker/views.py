import json
import os
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import SymptomCheck


@login_required
def checker_page(request):
    """Renders the multi-step symptom input wizard."""
    recent_checks = SymptomCheck.objects.filter(user=request.user)[:5]
    return render(request, 'symptom_checker/checker.html', {
        'recent_checks': recent_checks,
    })


@login_required
@csrf_exempt
def analyze_symptoms(request):
    """AJAX endpoint: sends structured symptom data to Gemini for analysis."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method.'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON.'}, status=400)

    body_area = data.get('body_area', '')
    symptoms = data.get('symptoms', [])
    additional_info = data.get('additional_info', '')
    duration = data.get('duration', '')
    severity = data.get('severity', 5)
    age = data.get('age')
    gender = data.get('gender', '')

    if not symptoms:
        return JsonResponse({'error': 'Please select at least one symptom.'}, status=400)

    # Build the prompt
    user = request.user
    symptoms_text = ', '.join(symptoms)

    prompt = f"""You are a professional AI medical symptom analyzer for the Prana AI application.
Analyze the following patient symptoms and provide a detailed assessment.

Patient Information:
- Age: {age or 'Not specified'}
- Gender: {gender or 'Not specified'}
- Body Area: {body_area}
- Symptoms: {symptoms_text}
- Duration: {duration}
- Severity (1-10): {severity}
- Additional Info: {additional_info or 'None'}

Please respond in the following JSON format ONLY, with no extra text:
{{
    "urgency": "<low|medium|high|emergency>",
    "urgency_description": "<brief urgency explanation>",
    "possible_conditions": [
        {{
            "name": "<condition name>",
            "probability": "<High|Medium|Low>",
            "description": "<brief description>"
        }}
    ],
    "recommendations": ["<recommendation 1>", "<recommendation 2>", "<recommendation 3>"],
    "when_to_see_doctor": "<specific guidance on when to seek professional help>",
    "home_remedies": ["<remedy 1>", "<remedy 2>"],
    "disclaimer": "This analysis is for educational purposes only. It is not a medical diagnosis. Always consult a qualified healthcare professional for proper evaluation and treatment."
}}

IMPORTANT RULES:
1. Be thorough but concise.
2. Always err on the side of caution — if symptoms could indicate something serious, recommend seeing a doctor.
3. Include at most 4 possible conditions, ordered by relevance.
4. Always include the disclaimer."""

    def get_groq_fallback_response_json(prompt_text):
        from groq import Groq
        from django.conf import settings as django_settings
        from dotenv import load_dotenv
        load_dotenv(os.path.join(django_settings.BASE_DIR, '.env'))
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

        try:
            response = model.generate_content(prompt)
            response_text = response.text.strip()
        except Exception as gemini_err:
            error_msg = str(gemini_err).lower()
            if "429" in error_msg or "quota" in error_msg or "rate limit" in error_msg or "exhausted" in error_msg:
                print("Gemini limit reached. Falling back to Groq for Symptom Checker.")
                response_text = get_groq_fallback_response_json(prompt).strip()
            else:
                raise gemini_err

        # Parse JSON from response (handle markdown code blocks)
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1])

        result = json.loads(response_text)

        # Save to database
        SymptomCheck.objects.create(
            user=request.user,
            body_area=body_area,
            symptoms_json=json.dumps(symptoms),
            additional_info=additional_info,
            duration=duration,
            severity=severity,
            age=age,
            gender=gender,
            ai_response=json.dumps(result),
            urgency_level=result.get('urgency', 'medium'),
            possible_conditions=json.dumps(result.get('possible_conditions', [])),
        )

        return JsonResponse(result)

    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        return JsonResponse({
            'urgency': 'medium',
            'urgency_description': 'Unable to fully parse AI response. Please consult a healthcare professional.',
            'possible_conditions': [],
            'recommendations': ['Please consult a healthcare professional for proper evaluation.'],
            'when_to_see_doctor': 'If symptoms persist or worsen, see a doctor immediately.',
            'home_remedies': [],
            'disclaimer': 'This is not a medical diagnosis. Always consult a qualified healthcare professional.',
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def check_history(request):
    """View past symptom checks."""
    checks = SymptomCheck.objects.filter(user=request.user)
    return render(request, 'symptom_checker/history.html', {'checks': checks})
