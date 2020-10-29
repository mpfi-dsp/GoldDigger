from GDapp.tasks import celery_timer_task
from GDapp.prediction.FrontEndUpdater import FrontEndUpdater
from GDapp.apps import GdappConfig
from django.shortcuts import render, redirect
from .forms import EMImageForm
from django.core.files.storage import FileSystemStorage

import csv
from django.http import HttpResponse
from .models import EMImage

import sys

# def start_gold_digger(obj):
#     if obj.mask.name == '':
#         mask = None
#     else:
#         mask = obj.mask.path
#     gold_digger = GdappConfig.gold_particle_detector
#     # front_end_updater = FrontEndUpdater(obj.id)
#     gold_digger(obj.id)
#     # gold_digger(obj.trained_model, obj.image.path, obj.particle_groups, mask, front_end_updater)

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
    pk = inputs['pk']
    gold_digger = GdappConfig.gold_particle_detector
    gold_digger(pk)
    return render(request, 'GDapp/run_gd.html', {'pk':pk})


# attempt to make a downloadable csv
def export(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)

