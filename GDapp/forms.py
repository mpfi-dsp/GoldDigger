from django import forms
from .models import *


class EMImageForm(forms.ModelForm):

    class Meta:
        model = EMImage
        widgets = {'preloaded_pk': forms.HiddenInput()}
        fields = ['trained_model', 'particle_groups', 'threshold_string', 'preloaded_pk']
        labels = {'trained_model': 'Trained model', 'threshold_string': 'Cutoff string'}

        #fields = ['image', 'mask', 'trained_model', 'particle_groups', 'threshold_string']
