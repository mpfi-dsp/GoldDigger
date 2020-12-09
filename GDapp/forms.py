from django import forms
from .models import *


class EMImageForm(forms.ModelForm):

    class Meta:
        model = EMImage
        widgets = {'preloaded_pk': forms.HiddenInput()}
        fields = ['trained_model', 'particle_groups', 'preloaded_pk']
