from django.db import models

class User(models.Model):
    username = models.TextField()
    password = models.TextField()
    state=models.IntegerField()
    level= models.IntegerField()

