from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DiseaseScan
from .forms import ScanUploadForm
import google.generativeai as genai
import PIL.Image
import os
from django.conf import settings
from dotenv import load_dotenv

def get_gemini_model():
    load_dotenv(os.path.join(settings.BASE_DIR, '.env'))
    api_key = os.environ.get('GEMINI_API_KEY')
    if api_key:
        api_key = api_key.strip('"').strip("'")
        genai.configure(api_key=api_key)
        # Using gemini-2.5-flash as it's the recommended multimodal model
        return genai.GenerativeModel('gemini-2.5-flash')
    return None

@login_required
def upload_scan(request):
    if request.method == 'POST':
        form = ScanUploadForm(request.POST, request.FILES)
        if form.is_valid():
            scan = form.save(commit=False)
            scan.user = request.user
            scan.save()
            return redirect('disease_detection:analyze', scan_id=scan.id)
    else:
        form = ScanUploadForm()
    
    return render(request, 'disease_detection/upload.html', {'form': form})

@login_required
def analyze_scan(request, scan_id):
    scan = get_object_or_404(DiseaseScan, id=scan_id, user=request.user)
    
    # If already analyzed, just show the result
    if scan.result_text:
        return render(request, 'disease_detection/result.html', {'scan': scan})
        
    try:
        model = get_gemini_model()
        if not model:
            messages.error(request, "Gemini API key is missing or invalid.")
            return redirect('disease_detection:upload')
            
        img_path = scan.image.path
        img = PIL.Image.open(img_path)
        
        prompt = """
        You are a highly advanced AI medical assistant. Please analyze this medical image carefully.
        Identify any visible anomalies, signs of diseases, or conditions. 
        Format your response nicely with markdown (e.g., use headings, bullet points).
        
        Based on the detected condition, please provide educational information broken down into these exact sections:
        
        1. General Medical Care: Typical treatment approaches and recovery expectations.
        2. Homeopathy: Clearly label this as *Alternative Information Only*. Explicitly mention that scientific evidence for homeopathy differs from standard medical care, and its efficacy is not scientifically proven. 
        3. Lifestyle Advice: Provide specific recommendations on:
           - Foods to eat
           - Foods to avoid
           - Water intake
           - Sleep recommendations
           - Exercise suggestions
           - Stress management

        IMPORTANT: Include a strong disclaimer at the very beginning and end stating that this information is purely educational and not a substitute for professional medical advice. Always encourage consulting a qualified healthcare professional.
        """
        
        response = model.generate_content([prompt, img])
        
        scan.result_text = response.text
        scan.save()
        
        messages.success(request, "Analysis complete!")
        return render(request, 'disease_detection/result.html', {'scan': scan})
        
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            messages.error(request, "Our AI servers are currently busy processing too many requests. Please wait a moment and refresh this page.")
        else:
            messages.error(request, f"Failed to analyze image: {error_msg}")
        # Allow them to see the page with the error and a retry button
        return render(request, 'disease_detection/result.html', {'scan': scan, 'error': error_msg})

@login_required
def scan_history(request):
    scans = DiseaseScan.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'disease_detection/history.html', {'scans': scans})
