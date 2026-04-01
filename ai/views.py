import os
os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"   # ✅ FFmpeg fix

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ExtractedInformation
import json
import tempfile
from groq import Groq

# 🔥 Load Whisper (fast model)



# ------------------- WELCOME -------------------

def welcome(request):
    return JsonResponse({
        "message": "welcome to english learning app"
    })






client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ------------------- SPEECH -------------------

@csrf_exempt
def speech_to_text(request):
   
    print("🔥 API HIT")

    if request.method == "POST":
        try:
            audio_file = request.FILES.get('file')

            if not audio_file:
                return JsonResponse({"error": "No file uploaded"}, status=400)

            # 🎧 Save temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as temp:
                for chunk in audio_file.chunks():
                    temp.write(chunk)
                temp_path = temp.name

            print("🎧 File saved:", temp_path)

            # 🤖 Whisper
            print("🤖 Running whisper...")
            with open(temp_path, "rb") as f:
                transcription = client.audio.transcriptions.create(
                    file=f,
                    model="whisper-large-v3")
            
            
            print("✅ Whisper done")

            text = transcription.get("text", "")
            print("📝 TEXT:", text)

            # 🤖 AI response
            ai_response = teaching(None, text)

            # 🗑️ delete file
            os.remove(temp_path)

            return JsonResponse({
                "text": text,
                "ai_response": ai_response
            })

        except Exception as e:
            print("❌ ERROR:", str(e))
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


# ------------------- SAVE INFO -------------------

@csrf_exempt
def save_extracted_info(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            obj, created = ExtractedInformation.objects.update_or_create(
                user=request.user,
                defaults={
                    "language": data.get("language"),
                    "purpose": data.get("purpose"),
                    "level": data.get("level"),
                    "malayalam": data.get("malayalam"),
                    "malayalam_mode": data.get("malayalamMode"),
                }
            )

            return JsonResponse({
                "message": "Created" if created else "Updated",
                "id": obj.id
            })

        except Exception as e:
            return JsonResponse({"error": str(e)})

    return JsonResponse({"error": "Invalid request"}, status=400)


# ------------------- STUDENT INFO -------------------

def get_student_info(user):
    try:
        if not user:
            return "Beginner student"

        data = ExtractedInformation.objects.get(user=user)
        name = user.username.split("@")[0]

        return f"""
        Name: {name}
        Purpose: {data.purpose}
        Level: {data.level}
        Malayalam Support: {data.malayalam}
        Malayalam Mode: {data.malayalam_mode}
        """

    except:
        return "Beginner student"


# ------------------- AI TEACHING -------------------

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

def teaching(user, user_input):

    print("🤖 AI INPUT:", user_input)

    template = """
You are a friendly and natural English speaking partner.

GOAL:
Help the user practice real-life English conversation.

=====================
STYLE
=====================
- Speak like a real human (casual and friendly)
- Keep replies SHORT (max 2 sentences)
- Use simple English
- Sound natural for voice (text-to-speech friendly)
- Do NOT sound like a strict teacher

=====================
LANGUAGE RULE
=====================
- Main conversation MUST be in English
- If Malayalam Support = true OR Malayalam Mode = true:
  - Occasionally explain difficult words or sentences in Malayalam
  - Keep Malayalam explanation short
  - Do NOT switch fully to Malayalam

=====================
LEVEL RULE
=====================
- If beginner:
  - Use very simple words and short sentences
- If intermediate:
  - Use slightly better vocabulary

=====================
CORRECTION RULE
=====================
- If the user makes a mistake:
  - Correct it in ONE short sentence
  - Then continue the conversation naturally
- Ignore very small mistakes

=====================
CONVERSATION FLOW
=====================
- Respond to the user naturally
- Ask 1 simple follow-up question
- Keep conversation going

=====================
STRICT RULES
=====================
- Do NOT use symbols like #, *, or bullet points
- Do NOT give long explanations
- Keep everything short and clear

=====================
STUDENT INFO
=====================
{student_info}

=====================
USER
=====================
{input}
"""

    prompt = ChatPromptTemplate.from_template(template)

    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="openai/gpt-oss-20b"
    )

    chain = prompt | llm

    student_info = get_student_info(user)

    try:
        response = chain.invoke({
            "input": user_input,
            "student_info": student_info
        })

        return response.content

    except Exception as e:
        print("❌ AI ERROR:", str(e))
        return "Sorry, I couldn't respond right now."