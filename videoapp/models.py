from django.db import models

# Create your models here.
class Video(models.Model):
    title = models.CharField(max_length=255)
    original_video = models.FileField(upload_to='videos/',)
    transcript = models.JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.title