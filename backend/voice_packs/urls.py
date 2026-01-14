from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_audio, name='upload_audio'),
    path('generate/', views.generate_voice_pack, name='generate_voice_pack'),
    path('health/', views.health_check, name='health_check'),
]