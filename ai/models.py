from django.db import models
from django.conf import settings

class ExtractedInformation(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    language = models.CharField(max_length=50)
    purpose  = models.CharField(max_length=100)
    level = models.CharField(max_length=100)
    malayalam = models.CharField(max_length=10)
    malayalam_mode = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.language}-{self.level}"