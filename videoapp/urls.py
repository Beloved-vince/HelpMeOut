from django.urls import path
from .views import VideoTranscriptView

urlpatterns = [
    path('upload/', VideoTranscriptView.as_view(), name='video-upload'),

]
