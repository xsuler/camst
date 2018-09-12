from django.db import models


class Alarm(models.Model):
    content = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
