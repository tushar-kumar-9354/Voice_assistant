# assistant/views.py (CORRECTED IMPORTS)
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, FileResponse  # ✅ Correct import
from django.views.decorators.csrf import csrf_exempt
# Correct async imports
from django.conf import settings
import json
import os
import asyncio
import subprocess
import google.generativeai as genai
import edge_tts
from .models import ChatHistory
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import json
import traceback
import edge_tts
import os, json, subprocess, uuid
from django.shortcuts  import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai


genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

def index(request):
    return render(request, 'assistant/index.html')



# Load your GEMINI_API_KEY from env in settings.py or .env
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

def index(request):
    return render(request, 'assistant/index.html')


import os, json, subprocess, uuid
from django.shortcuts     import render
from django.http          import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai

# Load your GEMINI_API_KEY from env in settings.py or .env
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

def index(request):
    return render(request, 'assistant/index.html')


def get_history(request):
    session_id = request.session.session_key
    if session_id:
        chats = ChatHistory.objects.filter(session_id=session_id).order_by('-timestamp')
        history = [{"prompt": c.prompt, "response": c.response} for c in chats]
        return JsonResponse({"history": history})
    return JsonResponse({"history": []})

# Convert text to speech using Edge TTS
def text_to_speech(request):
    text = request.GET.get('text', '')

    async def generate_audio():
        communicate = edge_tts.Communicate(text, "en-IN-NeerjaNeural")
        await communicate.save(settings.VOICE_FILE_PATH)

    # Run the async function properly and wait until it's fully done
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(generate_audio())
    loop.close()

    # Ensure file is now fully written
    if os.path.exists(settings.VOICE_FILE_PATH):
        return FileResponse(open(settings.VOICE_FILE_PATH, 'rb'), content_type='audio/mpeg')
    else:
        return JsonResponse({'error': 'Audio file not generated.'}, status=500)

def get_audio_bytes(text):
    try:
        output_file = "static/audio/response.mp3"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        subprocess.run([
            "edge-tts", "--text", text,
            "--voice", "en-US-AriaNeural",
            "--write-media", output_file
        ], check=True)

        with open(output_file, "rb") as f:
            audio_data = f.read()
            print("Audio Bytes Length:", len(audio_data))
            return audio_data

    except Exception as e:
        print("Audio generation error:", str(e))
        return b""
# Temporary test route
@csrf_exempt
def test_connection(request):
    try:
        # Test Gemini
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content("Test connection")
        
        # Test TTS
        communicate = edge_tts.Communicate("Test audio", "en-US-AriaNeural")
        
        return JsonResponse({
            'gemini_working': bool(response.text),
            'tts_working': True
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
import os, json, subprocess, uuid
from django.shortcuts     import render
from django.http          import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai

# Load your GEMINI_API_KEY from env in settings.py or .env
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

def index(request):
    return render(request, 'assistant/index.html')

@csrf_exempt
def ask_gemini(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        data   = json.loads(request.body)
        prompt = data.get('prompt','').strip()
        if not prompt:
            return JsonResponse({'error': 'Empty prompt'}, status=400)

        # 1️⃣ Get Gemini text reply
        resp  = model.generate_content(prompt)
        reply = resp.text.strip()
        if not reply:
            return JsonResponse({'error': 'No reply from Gemini'}, status=500)

        # 2️⃣ Prepare a unique filename
        filename = f"{uuid.uuid4().hex}.mp3"
        audio_dir = os.path.join('static','assistant','audio')
        os.makedirs(audio_dir, exist_ok=True)
        path = os.path.join(audio_dir, filename)

        # 3️⃣ Run Edge-TTS CLI to write the file
        subprocess.run([
            "edge-tts",
            "--text", reply,
            "--voice", "en-US-AriaNeural",
            "--write-media", path
        ], check=True)

        # 4️⃣ Read it back and return
        with open(path, 'rb') as f:
            data = f.read()
        return HttpResponse(data, content_type='audio/mpeg')

    except subprocess.CalledProcessError:
        return JsonResponse({'error': 'TTS generation failed'}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
