from django import forms
from .models import *
import config

local_file_args = dict(path='/usr/src/local-images',
                       required=False,
                       help_text=config.LOCAL_IMAGE_FOLDER,
                       allow_folders=True)


class EMImageForm(forms.ModelForm):

    class Meta:
        model = EMImage
        widgets = {'preloaded_pk': forms.HiddenInput()}
        fields = ['trained_model', 'particle_groups', 'threshold_string',
                  'preloaded_pk']
        labels = {'trained_model': 'Trained model', 'threshold_string': 'Cutoff string',
                  }

        #fields = ['image', 'mask', 'trained_model', 'particle_groups', 'threshold_string']


class LocalFilesForm(forms.Form):
    # necessary to have this separate so it reloads correctly
    local_image = forms.FilePathField(**local_file_args)
    local_mask = forms.FilePathField(**local_file_args)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['local_image'] = forms.FilePathField(label='Local image file (used if no file is uploaded)',
                                                         **local_file_args)
        self.fields['local_mask'] = forms.FilePathField(label='Local mask (optional, used if no mask file is uploaded)',
                                                        **local_file_args)
        self.fields['local_image'].widget.attrs['class'] = 'form-control'
        self.fields['local_mask'].widget.attrs['class'] = 'form-control'
