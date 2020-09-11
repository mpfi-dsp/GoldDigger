from django.db import models
from django import forms


# Create your models here.
class Profile(models.Model):
    profile = models.ImageField(upload_to="Input/")





