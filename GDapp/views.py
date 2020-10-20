from django.shortcuts import render, redirect
from .forms import EMImageForm
from django.core.files.storage import FileSystemStorage

import csv
from django.http import HttpResponse
from .models import EMImage

import sys
from .tasks import gd_task

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
    task = gd_task.delay(obj.trained_model, obj.image.path)
    return render(request, 'GDapp/run_gd.html', {'task_id': task.task_id})


# attempt to make a downloadable csv
def export(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)

