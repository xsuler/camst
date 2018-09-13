from django.db import models

class User(models.Model):
    username = models.TextField()
    password = models.TextField()
    state=models.IntegerField(default=0)
    level= models.IntegerField(default=1)

