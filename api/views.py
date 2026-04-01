from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
import json

User = get_user_model()

@csrf_exempt
def signup(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            email = data.get("email")
            password = data.get("password")

            if not email or not password:
                return JsonResponse({"error": "Email and password required"}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({"error": "User already exists"}, status=400)

            user = User.objects.create_user(
                username=email,  # ✅ username = email
                email=email,
                password=password
            )

            token, _ = Token.objects.get_or_create(user=user)

            return JsonResponse({
                "token": token.key,
                "message": "User created"
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)



from django.contrib.auth import authenticate

@csrf_exempt
def login(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            email = data.get("email")
            password = data.get("password")

            if not email or not password:
                return JsonResponse({"error": "Email and password required"}, status=400)

            user = authenticate(username=email, password=password)

            if not user:
                return JsonResponse({"error": "Invalid credentials"}, status=400)

            token, _ = Token.objects.get_or_create(user=user)

            return JsonResponse({
                "token": token.key,
                "message": "Login successful"
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)