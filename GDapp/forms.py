from django import forms
from .models import *
import config

local_file_args = dict(path='/usr/src/local-images',
                       required=False)
                       #help_text=config.LOCAL_IMAGE_FOLDER)


class EMImageForm(forms.ModelForm):
    '''Fills out params in EMImage object.'''

    class Meta:
        model = EMImage
        widgets = {'preloaded_pk': forms.HiddenInput()}
        fields = ['trained_model', 'particle_groups', 'threshold_string', 'thresh_sens',
                  'preloaded_pk']
        labels = {'trained_model': 'Trained model', 'threshold_string': 'Cutoff string', 'thresh_sens': 'Threshold sensitivity'
                  }


class LocalFilesForm(forms.Form):
    '''Files for local upload.'''
    # necessary to have this separate so it reloads correctly
    local_image = forms.FilePathField(**local_file_args)
    #local_mask = forms.FilePathField(**local_file_args)
    local_mask = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['local_image'] = forms.FilePathField(label='Local image file or folder of images and masks',
                                                         **local_file_args, allow_folders=True, allow_files=False)
        #self.fields['local_mask'] = forms.FilePathField(label='Local mask file (optional)',
        #                                                **local_file_args, allow_folders=False)
        self.fields['local_mask'] = None
        self.fields['local_image'].widget.attrs['class'] = 'form-control'
        self.fields['local_mask'].widget.attrs['class'] = 'form-control'
