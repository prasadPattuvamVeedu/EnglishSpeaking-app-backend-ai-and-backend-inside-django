from django.urls import path
from . import views

urlpatterns = [
    path("", views.welcome),
    path("extract/",views.ExtractedInformation),
    path("speech_to_text/",views.speech_to_text),
]