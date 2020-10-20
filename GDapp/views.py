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
            form.save()
            # return redirect('success')
    else:
        form = EMImageForm()
    return render(request, 'GDapp/upload.html', {'form': form})


def run_gd(request):
    model = request.POST.get('model')
    # out = run([sys.executable, 'run.py', inp], shell=False, stdout=PIPE)
    # print(out)
    task = gd_task.delay(model)
    return render(request, 'GDapp/run_gd.html', {'task_id': task.task_id})


# attempt to make a downloadable csv
def export(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)

