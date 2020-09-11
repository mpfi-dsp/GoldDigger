from django.shortcuts import render, redirect
from .forms import ProfileForm
from django.core.files.storage import FileSystemStorage

import csv
from django.http import HttpResponse
from .models import Profile

from subprocess import run, PIPE
import sys


# Create your views here.
def home(request):
    return render(request, 'GDapp/home.html')


# url doesn't work if the file name has spaces in it
# def upload(request):
#     context = {}
#     if request.method == 'POST':
#         uploaded_file = request.FILES['document']
#         fs = FileSystemStorage()
#         name = fs.save(uploaded_file.name, uploaded_file)
#         url = fs.url(name)
#         context['url'] = fs.url(name)
#     return render(request, 'GDapp/upload.html', context)


def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            # return redirect('success')
    else:
        form = ProfileForm()
    return render(request, 'GDapp/upload.html', {'form': form})


# def success(request):
#     return HttpResponse('successfully uploaded')


def external(request):
    inp = request.POST.get('model')
    out = run([sys.executable, 'run.py', inp], shell=False, stdout=PIPE)
    print(out)
    return render(request, 'GDapp/upload.html')


# attempt to make a downloadable csv
def export(request):
    response = HttpResponse(content_type='text/csv')

    writer = csv.writer(response)
