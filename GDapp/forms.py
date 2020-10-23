from django import forms
from .models import *


class EMImageForm(forms.ModelForm):

    class Meta:
        model = EMImage
<<<<<<< HEAD
        fields = ['image', 'mask', 'trained_model']
=======
        fields = ['image', 'trained_model']
>>>>>>> c9cc1c8e8f296c429e30f4b03ff400a355e61b45
