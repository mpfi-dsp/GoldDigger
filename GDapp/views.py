from django.shortcuts import render, redirect
from .forms import EMImageForm
from django.core.files.storage import FileSystemStorage

import csv
from django.http import HttpResponse
from .models import EMImage

import sys

# Create your views here.
def home(request):
    return render(request, 'GDapp/home.html')

def image_view(request):
    if request.method == 'POST':
        form = EMImageForm(request.POST, request.FILES)
        
        if form.is_valid():
            instance = form.save()
            return run_gd(request, {'id':instance.id})
    else:
        form = EMImageForm()
    return render(request, 'GDapp/upload.html', {'form': form})


def run_gd(request, inputs):
    obj = EMImage.objects.get(pk=inputs['id'])
    if obj.mask.name == '':
        mask = None
    else:
        mask = obj.mask.path
    print('run task here')
    return render(request, 'GDapp/run_gd.html')


# attempt to make a downloadable csv
def export(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)

