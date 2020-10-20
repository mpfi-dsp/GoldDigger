from django import forms
from .models import *


class EMImageForm(forms.ModelForm):

    class Meta:
        model = EMImage
        fields = ['image', 'trained_model']
