from django.urls import path
from . import views


urlpatterns = [
    path('', views.text_to_speech, name='text_to_speech'),
    path('delete/', views.delete_audio_directory, name='delete_audio_directory')
]
