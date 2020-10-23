from django.db import models
from django import forms

TRAINED_MODEL_CHOICES = [
    ('43kGoldDigger', '43kGoldDigger'),
    ('87kGoldDigger', '87kGoldDigger')
]

class EMImage(models.Model):
    image = models.FileField(upload_to="Input/")
<<<<<<< HEAD
    mask = models.FileField(upload_to="Mask/", blank=True)
=======
>>>>>>> c9cc1c8e8f296c429e30f4b03ff400a355e61b45
    trained_model = models.CharField(max_length=100,
                                     blank=False,
                                     default='87kGoldDigger',
                                     choices=TRAINED_MODEL_CHOICES)
