import os
import json
import google.generativeai as genai
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

def get_gemini_model():
    from django.conf import settings
    from dotenv import load_dotenv
    load_dotenv(os.path.join(settings.BASE_DIR, '.env'))
    api_key = os.environ.get('GEMINI_API_KEY')
    if api_key:
        # Strip quotes if they were accidentally added
        api_key = api_key.strip('"').strip("'")
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-2.5-flash')
    return None

@login_required
def chat_view(request):
    """Render the chat interface."""
    from django.conf import settings
    from dotenv import load_dotenv
    load_dotenv(os.path.join(settings.BASE_DIR, '.env'))
    api_key = os.environ.get('GEMINI_API_KEY')
    return render(request, 'chatbot/chat.html', {'api_key_set': bool(api_key)})

from django.http import StreamingHttpResponse

def get_groq_fallback_stream(prompt):
    import os
    from groq import Groq
    from django.conf import settings
    from dotenv import load_dotenv
    load_dotenv(os.path.join(settings.BASE_DIR, '.env'))
    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key:
        raise ValueError("Groq API key is not configured for fallback.")
    client = Groq(api_key=api_key)
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1024,
        stream=True
    )
    for chunk in completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

def gemini_stream(model, prompt):
    try:
        response = model.generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as gemini_err:
        error_msg = str(gemini_err).lower()
        if "429" in error_msg or "quota" in error_msg or "rate limit" in error_msg or "exhausted" in error_msg:
            print("Gemini limit reached. Falling back to Groq for Chatbot Streaming.")
            try:
                for text in get_groq_fallback_stream(prompt):
                    yield text
            except Exception as groq_err:
                yield f"\n\n[System Error: Groq fallback failed - {str(groq_err)}]"
        else:
            yield f"\n\n[System Error: {str(gemini_err)}]"

@login_required
@csrf_exempt
def send_message(request):
    """Handle incoming messages and stream response."""
    if request.method == 'POST':
        model = get_gemini_model()
        if not model:
            return JsonResponse({'error': 'Gemini API key is not configured or invalid.'}, status=500)
            
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            if not user_message:
                return JsonResponse({'error': 'Message cannot be empty.'}, status=400)
                
            # Define system instructions for the health chatbot
            prompt = f"You are a helpful, professional, and knowledgeable AI health assistant for the Prana AI application. Answer the user's health-related query. Keep responses concise but informative. Please note that you cannot give definitive medical diagnoses. User message: {user_message}"
            
            return StreamingHttpResponse(gemini_stream(model, prompt), content_type='text/plain')
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Invalid request method.'}, status=405)
