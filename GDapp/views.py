from GDapp.apps import GdappConfig
from django.shortcuts import render, redirect
from .forms import EMImageForm
from django.core.files.storage import FileSystemStorage

import csv
from django.http import HttpResponse
from .models import EMImage

import sys

def start_gold_digger(obj):
    gold_digger = GdappConfig.gold_particle_detector
    gold_digger()

# Create your views here.
def home(request):
    return render(request, 'GDapp/home.html')

def image_view(request):
    if request.method == 'POST':
        form = EMImageForm(request.POST, request.FILES)
        
        if form.is_valid():
            instance = form.save()
            return run_gd(request, {'pk':instance.id})
    else:
        form = EMImageForm()
    return render(request, 'GDapp/upload.html', {'form': form})


def run_gd(request, inputs):
    obj = EMImage.objects.get(pk=inputs['pk'])
    if obj.mask.name == '':
        mask = None
    else:
        mask = obj.mask.path
    print('run task here')
    start_gold_digger(obj)
    return render(request, 'GDapp/run_gd.html', {'pk':obj.id})


# attempt to make a downloadable csv
def export(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)

