from django.db import models


class Alarm(models.Model):
    content = models.TextField()
    time = models.DateTimeField(auto_now_add=True)


class Region(models.Model):
    name = models.TextField()
    cover = models.FloatField()
    delay = models.FloatField()
    x = models.IntegerField()
    y = models.IntegerField()
    w = models.IntegerField()
    h = models.IntegerField()


class Cam(models.Model):
    name = models.TextField()
    addr = models.TextField()
