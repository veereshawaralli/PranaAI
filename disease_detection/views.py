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

def get_groq_vision_fallback_from_path(prompt_text, img_path):
    import base64
    from groq import Groq
    load_dotenv(os.path.join(settings.BASE_DIR, '.env'))
    groq_api_key = os.environ.get('GROQ_API_KEY')
    if not groq_api_key:
        raise ValueError("Groq API key is not configured.")
    
    with open(img_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    client = Groq(api_key=groq_api_key)
    completion = client.chat.completions.create(
        model="llama-3.2-11b-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        temperature=0.7,
        max_tokens=1024
    )
    return completion.choices[0].message.content

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
        
        Please structure your response into two main parts:
        
        # 1. Quick Summary (Short Answer)
        Provide a brief, 2-3 sentence overview of the findings and the most immediate recommendation for quick reading. 
        CRITICAL: Write this section in plain, simple English that a normal person without a medical background can easily understand. Avoid complex medical jargon here.
        
        # 2. Detailed Analysis (Long Answer)
        Based on the detected condition, please provide comprehensive educational information broken down into these exact sections:
        
        - Detailed Findings: A detailed description of the visible anatomical structures and abnormalities.
        - General Medical Care: Typical treatment approaches and recovery expectations.
        - Homeopathy: Clearly label this as *Alternative Information Only*. Explicitly mention that scientific evidence for homeopathy differs from standard medical care, and its efficacy is not scientifically proven. 
        - Lifestyle Advice: Provide specific recommendations on:
           - Foods to eat
           - Foods to avoid
           - Water intake
           - Sleep recommendations
           - Exercise suggestions
           - Stress management
        """
        
        try:
            response = model.generate_content([prompt, img])
            scan.result_text = response.text
        except Exception as gemini_err:
            error_msg = str(gemini_err).lower()
            if "429" in error_msg or "quota" in error_msg or "rate limit" in error_msg or "exhausted" in error_msg:
                print("Gemini limit reached. Falling back to Groq for Disease Detection.")
                scan.result_text = get_groq_vision_fallback_from_path(prompt, img_path)
            else:
                raise gemini_err
        
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
