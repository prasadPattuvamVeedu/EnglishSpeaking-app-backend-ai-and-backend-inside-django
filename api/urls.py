from django.urls import path
from .views import signup, login,welcome

urlpatterns = [
    path('',welcome),
    path("signup/", signup),
    path("login/", login),
]