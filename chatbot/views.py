import os
import json
import google.generativeai as genai
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

# Initialize Gemini if key is available
api_key = os.environ.get('GEMINI_API_KEY')
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

@login_required
def chat_view(request):
    """Render the chat interface."""
    return render(request, 'chatbot/chat.html', {'api_key_set': bool(api_key)})

@login_required
@csrf_exempt
def send_message(request):
    """Handle incoming messages and return Gemini response."""
    if request.method == 'POST':
        if not model:
            return JsonResponse({'error': 'Gemini API key is not configured.'}, status=500)
            
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
