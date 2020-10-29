from django.db import models
from django import forms
from django.core.validators import MinValueValidator

TRAINED_MODEL_CHOICES = [
    ('43kGoldDigger', '43kGoldDigger'),
    ('87kGoldDigger', '87kGoldDigger')
]

class EMImage(models.Model):
    image = models.FileField(upload_to="Input/", blank=True, default='')
    mask = models.FileField(upload_to="Mask/", blank=True)
    particle_groups = models.IntegerField(blank=False, default=1, validators=[MinValueValidator(1)])
    trained_model = models.CharField(max_length=100,
                                     blank=False,
                                     default='87kGoldDigger',
                                     choices=TRAINED_MODEL_CHOICES)
