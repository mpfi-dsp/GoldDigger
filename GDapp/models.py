from django.db import models
from django import forms


# Create your models here.
class EMImage(models.Model):
    image = models.FileField(upload_to="Input/")
