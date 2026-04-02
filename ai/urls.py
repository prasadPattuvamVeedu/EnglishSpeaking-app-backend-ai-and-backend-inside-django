from django.urls import path
from . import views

urlpatterns = [
   
    path("extract/",views.ExtractedInformation),
    path("speech_to_text/",views.speech_to_text),
]