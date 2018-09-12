from django.db import models
import datetime

class Alarm(models.Model):
    content= models.TextField()
    time=models.DateTimeField(auto_now_add=True)
