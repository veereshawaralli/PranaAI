import os
import json
import re

import google.generativeai as genai
import PIL.Image
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

from .forms import TextTranslationForm, DocumentTranslationForm, LANGUAGE_CHOICES
from .models import TranslationHistory


# ──────────────────────────────────────
# Helpers
# ──────────────────────────────────────

def _get_gemini_model():
    """Return a configured Gemini GenerativeModel, or None."""
    load_dotenv(os.path.join(settings.BASE_DIR, '.env'))
    api_key = os.environ.get('GEMINI_API_KEY')
    if api_key:
        api_key = api_key.strip('"').strip("'")
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-2.5-flash')
    return None


def _clean_json_response(text: str) -> str:
    """Strip markdown code-fence wrappers that the model sometimes adds."""
    text = re.sub(r'^```json', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^```', '', text)
    text = re.sub(r'```$', '', text)
    return text.strip()


def _build_text_prompt(text: str, target_language: str) -> str:
    return f"""You are a professional medical translator. Translate the following medical text into {target_language}.

Return ONLY a JSON object with exactly these keys (no markdown, no backticks):
{{
  "translated_text": "... the full translation in {target_language} ...",
  "plain_explanation": "... a plain-language summary that explains any complex medical jargon in simple {target_language}, suitable for a patient with no medical background ..."
}}

Medical text to translate:
\"\"\"
{text}
\"\"\"
"""


def _build_document_prompt(target_language: str) -> str:
    return f"""You are a professional medical translator and document reader.

1. Extract ALL text visible in this medical document image.
2. Translate the extracted text into {target_language}.
3. Provide a plain-language explanation of the document in {target_language}.

Return ONLY a JSON object with exactly these keys (no markdown, no backticks):
{{
  "original_text": "... the extracted text from the image in its original language ...",
  "translated_text": "... the full translation in {target_language} ...",
  "plain_explanation": "... a plain-language summary in {target_language} that explains any complex medical terminology in simple words ..."
}}
"""


# ──────────────────────────────────────
# Views
# ──────────────────────────────────────

@login_required
def translator_home(request):
    """Landing page with 3 mode cards."""
    recent = TranslationHistory.objects.filter(user=request.user)[:5]
    return render(request, 'translator/home.html', {'recent_translations': recent})


@login_required
def text_translate(request):
    """Handle text translation via form POST."""
    result = None
    form = TextTranslationForm()

    if request.method == 'POST':
        form = TextTranslationForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text_to_translate']
            target_lang = form.cleaned_data['target_language']

            model = _get_gemini_model()
            if not model:
                messages.error(request, 'Gemini API key is not configured.')
                return redirect('translator:text_translate')

            try:
                prompt = _build_text_prompt(text, target_lang)
                response = model.generate_content(prompt)
                raw = _clean_json_response(response.text)
                data = json.loads(raw)

                result = {
                    'original_text': text,
                    'translated_text': data.get('translated_text', ''),
                    'plain_explanation': data.get('plain_explanation', ''),
                    'target_language': target_lang,
                }

                # Persist
                TranslationHistory.objects.create(
                    user=request.user,
                    translation_type='text',
                    target_language=target_lang,
                    original_text=text,
                    translated_text=result['translated_text'],
                    plain_explanation=result['plain_explanation'],
                )

            except Exception as e:
                error_msg = str(e)
                if '429' in error_msg or 'quota' in error_msg.lower():
                    messages.error(request, 'AI servers are busy. Please wait a moment and try again.')
                else:
                    messages.error(request, f'Translation failed: {error_msg}')
                return redirect('translator:text_translate')

    return render(request, 'translator/text_translate.html', {
        'form': form,
        'result': result,
        'languages': LANGUAGE_CHOICES,
    })


@login_required
def document_translate(request):
    """Handle document / image translation."""
    result = None
    form = DocumentTranslationForm()

    if request.method == 'POST':
        form = DocumentTranslationForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = request.FILES['document_image']
            target_lang = form.cleaned_data['target_language']

            model = _get_gemini_model()
            if not model:
                messages.error(request, 'Gemini API key is not configured.')
                return redirect('translator:document_translate')

            try:
                img = PIL.Image.open(image_file)
                prompt = _build_document_prompt(target_lang)
                response = model.generate_content([prompt, img])
                raw = _clean_json_response(response.text)
                data = json.loads(raw)

                # Save the image so we can display it
                history = TranslationHistory(
                    user=request.user,
                    translation_type='document',
                    target_language=target_lang,
                    original_text=data.get('original_text', ''),
                    translated_text=data.get('translated_text', ''),
                    plain_explanation=data.get('plain_explanation', ''),
                )
                image_file.seek(0)
                history.document_image.save(image_file.name, image_file, save=True)

                result = {
                    'original_text': data.get('original_text', ''),
                    'translated_text': data.get('translated_text', ''),
                    'plain_explanation': data.get('plain_explanation', ''),
                    'target_language': target_lang,
                    'image_url': history.document_image.url,
                }

            except Exception as e:
                error_msg = str(e)
                if '429' in error_msg or 'quota' in error_msg.lower():
                    messages.error(request, 'AI servers are busy. Please wait a moment and try again.')
                else:
                    messages.error(request, f'Translation failed: {error_msg}')
                return redirect('translator:document_translate')

    return render(request, 'translator/document_translate.html', {
        'form': form,
        'result': result,
    })


@login_required
def voice_translate(request):
    """Render the voice translation page. Speech recognition is client-side."""
    return render(request, 'translator/voice_translate.html', {
        'languages': LANGUAGE_CHOICES,
    })


@login_required
@csrf_exempt
def voice_translate_api(request):
    """AJAX endpoint: receives text captured by client-side speech recognition,
    translates via Gemini, and returns JSON."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

    try:
        body = json.loads(request.body)
        text = body.get('text', '').strip()
        target_lang = body.get('target_language', '').strip()

        if not text:
            return JsonResponse({'error': 'No text provided.'}, status=400)
        if not target_lang:
            return JsonResponse({'error': 'No target language selected.'}, status=400)

        model = _get_gemini_model()
        if not model:
            return JsonResponse({'error': 'Gemini API key is not configured.'}, status=500)

        prompt = _build_text_prompt(text, target_lang)
        response = model.generate_content(prompt)
        raw = _clean_json_response(response.text)
        data = json.loads(raw)

        # Persist
        TranslationHistory.objects.create(
            user=request.user,
            translation_type='voice',
            target_language=target_lang,
            original_text=text,
            translated_text=data.get('translated_text', ''),
            plain_explanation=data.get('plain_explanation', ''),
        )

        return JsonResponse({
            'translated_text': data.get('translated_text', ''),
            'plain_explanation': data.get('plain_explanation', ''),
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def translation_history(request):
    """Show all past translations."""
    translations = TranslationHistory.objects.filter(user=request.user)
    return render(request, 'translator/history.html', {'translations': translations})


@login_required
def delete_translation(request, pk):
    """Delete a single translation history entry."""
    entry = get_object_or_404(TranslationHistory, pk=pk, user=request.user)
    entry.delete()
    messages.success(request, 'Translation deleted.')
    return redirect('translator:history')
