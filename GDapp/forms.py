from django import forms
from .models import *


class EMImageForm(forms.ModelForm):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #reload local image and mask fields

    class Meta:
        model = EMImage
        widgets = {'preloaded_pk': forms.HiddenInput()}
        fields = ['trained_model', 'particle_groups', 'threshold_string', 'preloaded_pk', 'local_image', 'local_mask']
        labels = {'trained_model': 'Trained model', 'threshold_string': 'Cutoff string',
        'local_image': 'Local image file (used if no file is uploaded)',
        'local_mask': 'Local mask (used if no mask file is uploaded)',
        }

        #fields = ['image', 'mask', 'trained_model', 'particle_groups', 'threshold_string']
