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
        return genai.GenerativeModel('gemini-3.5-flash')
    return None

@login_required
def chat_view(request):
    """Render the chat interface."""
    from django.conf import settings
    from dotenv import load_dotenv
    load_dotenv(os.path.join(settings.BASE_DIR, '.env'))
    api_key = os.environ.get('GEMINI_API_KEY')
    return render(request, 'chatbot/chat.html', {'api_key_set': bool(api_key)})

@login_required
@csrf_exempt
def send_message(request):
    """Handle incoming messages and return Gemini response."""
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
            prompt = f"You are a helpful, professional, and knowledgeable AI health assistant for the MediBuddy application. Answer the user's health-related query. Keep responses concise but informative. Please note that you cannot give definitive medical diagnoses. User message: {user_message}"
            
            response = model.generate_content(prompt)
            
            return JsonResponse({
                'reply': response.text
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Invalid request method.'}, status=405)
