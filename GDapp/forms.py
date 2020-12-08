from django import forms
from .models import *


class EMImageForm(forms.ModelForm):

    class Meta:
        model = EMImage
        fields = ['image', 'mask', 'trained_model', 'particle_groups', 'threshold_string']
