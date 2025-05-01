from django.urls import path
from .views import index, ask_gemini

urlpatterns = [
    path('',       index,      name='index'),
    path('ask/',   ask_gemini, name='ask'),
]
