from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Video
from .serializers import VideoTranscriptSerializer
from moviepy.editor import VideoFileClip
import speech_recognition as sr
import json


class VideoTranscriptView(APIView):
    def post(self, request, format=None):
        video_file = request.FILES.get('original_video')
        title = request.data.get('title')
        if video_file:

            video_transcript = Video(title=title, original_video=video_file)
            video_transcript.save()

            # Extract transcript from the video
            video_path = video_transcript.original_video.path
            video = VideoFileClip(video_path)
            recognizer = sr.Recognizer()

            # Create a list to store text and timestamps
            text_with_timestamps = []

            # Define the interval duration and starting time
            interval_duration = 15  # seconds
            start_time = 0

            while start_time < video.duration:
                end_time = min(start_time + interval_duration, video.duration)
                audio = video.subclip(start_time, end_time).audio
                audio.write_audiofile('temp_audio.wav', codec='pcm_s16le')

                audio_path = 'temp_audio.wav'
                with sr.AudioFile(audio_path) as source:
                    recognizer.adjust_for_ambient_noise(source)
                    audio_data = recognizer.record(source)
                    try:
                        text = recognizer.recognize_google(audio_data)
                        formatted_start_time = f"{int(start_time // 60):d}.{int(start_time % 60):02d}"
                        text_with_timestamps.append({
                                        "timestamp": formatted_start_time,
                                        "text": text
                                    })
                    except sr.UnknownValueError:
                        print("Google Web Speech API could not understand the audio")
                    except sr.RequestError as e:
                        print("Could not request results from Google Web Speech API; {0}".format(e))

                start_time = end_time
                end_time = min(start_time + interval_duration, video.duration)  # Ensure the end time doesn't exceed the video duration

            
            # Save the text with timestamps in the desired format as a JSON file
            json_filename = 'extracted_text.json'
            with open(json_filename, 'w') as json_file:
                json.dump(text_with_timestamps, json_file, indent=4)

            # Store the transcript in the model
            transcript = '\n'.join([f"{entry['timestamp']} sec: {entry['text']}" for entry in text_with_timestamps])
            video_transcript.transcript = transcript
            video_transcript.save()

            serializer = VideoTranscriptSerializer(video_transcript)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response({'error': 'Video file not provided'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        video_transcripts = Video.objects.all()
        serializer = VideoTranscriptSerializer(video_transcripts, many=True)
        
        # Remove the 'transcript' field from each serialized object
        for data in serializer.data:
            data.pop('transcript', None)
        return Response(serializer.data, status=status.HTTP_200_OK)
