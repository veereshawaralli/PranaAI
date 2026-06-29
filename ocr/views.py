from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PrescriptionUploadForm
from dashboard.models import MedicineReminder
import google.generativeai as genai
import PIL.Image
import json
import os
from django.conf import settings
from dotenv import load_dotenv
import re

def get_gemini_model():
    load_dotenv(os.path.join(settings.BASE_DIR, '.env'))
    api_key = os.environ.get('GEMINI_API_KEY')
    if api_key:
        api_key = api_key.strip('"').strip("'")
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-2.5-flash')
    return None

@login_required
def upload_prescription(request):
    if request.method == 'POST':
        form = PrescriptionUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = request.FILES['image']
            
            try:
                img = PIL.Image.open(image_file)
                model = get_gemini_model()
                
                if not model:
                    messages.error(request, "Gemini API key is missing or invalid.")
                    return redirect('ocr:upload')
                
                prompt = """
                Analyze this medical prescription image. Extract all medicines mentioned.
                Return ONLY a JSON array of objects. Do not include markdown formatting or backticks.
                Each object must have exactly these keys:
                "medicine_name": the name of the medicine
                "dosage": the dosage (e.g. 500mg, 1 tablet)
                "frequency": how often to take it (e.g. Twice a day, Daily)
                
                If you cannot determine a field, return an empty string for that field.
                Example:
                [
                    {"medicine_name": "Paracetamol", "dosage": "500mg", "frequency": "Twice a day"}
                ]
                """
                
                response = model.generate_content([prompt, img])
                response_text = response.text.strip()
                
                # Try to clean up markdown if the AI includes it despite instructions
                response_text = re.sub(r'^```json', '', response_text, flags=re.IGNORECASE)
                response_text = re.sub(r'^```', '', response_text)
                response_text = re.sub(r'```$', '', response_text).strip()
                
                medicines = json.loads(response_text)
                
                if not isinstance(medicines, list):
                    raise ValueError("AI did not return a list.")
                
                # Store in session for the confirm view
                request.session['extracted_medicines'] = medicines
                return redirect('ocr:confirm')
                
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "quota" in error_msg.lower():
                    messages.error(request, "Our AI servers are currently busy processing too many requests. Please wait about 30 seconds and try again.")
                else:
                    messages.error(request, f"Failed to process image: {error_msg}")
                return redirect('ocr:upload')
    else:
        form = PrescriptionUploadForm()
        
    return render(request, 'ocr/upload.html', {'form': form})

@login_required
def confirm_prescription(request):
    medicines = request.session.get('extracted_medicines', [])
    
    if not medicines:
        messages.warning(request, "No medicines found to confirm.")
        return redirect('ocr:upload')
        
    if request.method == 'POST':
        # Process the form submission
        # We will receive arrays of medicine_name, dosage, frequency
        names = request.POST.getlist('medicine_name[]')
        dosages = request.POST.getlist('dosage[]')
        frequencies = request.POST.getlist('frequency[]')
        
        # We should also get a list of selected indices to save
        selected_indices = request.POST.getlist('save_item[]')
        
        saved_count = 0
        for i in selected_indices:
            idx = int(i)
            if idx < len(names):
                MedicineReminder.objects.create(
                    user=request.user,
                    medicine_name=names[idx],
                    dosage=dosages[idx],
                    frequency=frequencies[idx],
                    time="08:00:00" # Default time
                )
                saved_count += 1
                
        # Clear the session
        if 'extracted_medicines' in request.session:
            del request.session['extracted_medicines']
            
        messages.success(request, f"Successfully added {saved_count} medicine reminders!")
        return redirect('dashboard_home')
        
    return render(request, 'ocr/confirm.html', {'medicines': medicines})
