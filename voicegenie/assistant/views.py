from django.shortcuts import render
from django.http import HttpResponse, JsonResponse ,FileResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import google.generativeai as genai
import edge_tts
import asyncio
from .models import ChatHistory
from asgiref.sync import sync_to_async
from django.conf import settings
import subprocess
# Gemini setup
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

def index(request):
    return render(request, 'assistant/index.html')

@sync_to_async
def save_chat(session_id, prompt, reply):
    ChatHistory.objects.create(session_id=session_id, prompt=prompt, response=reply)

# Helper to collect async audio stream as bytes
async def get_audio_bytes(text):
    communicate = edge_tts.Communicate(text, "en-IN-NeerjaNeural")
    audio_data = b""
    async for chunk in communicate.stream():
        if "audio" in chunk:
            audio_data += chunk["audio"]
    return audio_data

@csrf_exempt
@csrf_exempt
def ask_gemini(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            prompt = data.get("prompt", "").strip()
            print("Received Prompt:", prompt)  # 👈 Check input

            if not prompt:
                return JsonResponse({"error": "Empty prompt"}, status=400)

            # Gemini response
            response = model.generate_content(prompt)
            reply = response.text.strip()
            print("Gemini Reply:", reply)  # 👈 Check Gemini output

            # Save session + chat
            session_id = request.session.session_key
            if not session_id:
                request.session.save()
                session_id = request.session.session_key

            asyncio.run(save_chat(session_id, prompt, reply))

            # Get audio bytes
            audio_bytes = asyncio.run(get_audio_bytes(reply))
            print("Audio Bytes Length:", len(audio_bytes))  # 👈 Check if audio is non-empty

            return HttpResponse(audio_bytes, content_type="audio/mpeg")

        except Exception as e:
            print("Error in /ask/:", str(e))  # 👈 Catch exception
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

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