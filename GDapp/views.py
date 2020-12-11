from GDapp.tasks import celery_timer_task
from GDapp.prediction.FrontEndUpdater import FrontEndUpdater
from GDapp.apps import GdappConfig
from django.shortcuts import render, redirect
from .forms import EMImageForm
from django.core.files.storage import FileSystemStorage
from django.views.generic.list import ListView
import csv
from django.http import HttpResponse
from .models import EMImage, MyChunkedUpload, add_image
from chunked_upload.views import ChunkedUploadView, ChunkedUploadCompleteView
from django.views.generic.base import TemplateView


import sys


# class ChunkedUploadDemo(TemplateView):
#     template_name = 'upload.html'

class MyChunkedUploadView(ChunkedUploadView):

    model = MyChunkedUpload
    field_name = 'the_file'

    def check_permissions(self, request):
        # Allow non authenticated users to make uploads
        pass


class MyChunkedUploadCompleteView(ChunkedUploadCompleteView):

    model = MyChunkedUpload

    def check_permissions(self, request):
        # Allow non authenticated users to make uploads
        pass

    def on_completion(self, uploaded_file, request):
        # Do something with the uploaded file. E.g.:
        # * Store the uploaded file on another model:
        # SomeModel.objects.create(user=request.user, file=uploaded_file)
        instance = EMImage.objects.create(image=uploaded_file)
        self.pk = instance.id
        # print(request.POST['upload_id'])
        # print(request.FILES or None)
        # * Pass it as an argument to a function:
        # function_that_process_file(uploaded_file)
        # print(uploaded_file)
        # pass
        # print(self.model.id)

    def get_response_data(self, chunked_upload, request):
        # form = EMImageForm(instance=self.instance)
        # return render(request, "GDapp/upload.html", {'form': form})
        # print(request.POST)
        return {'message': ("You successfully uploaded '%s' (%s bytes)!" %
                            (chunked_upload.filename, chunked_upload.offset)),
                'upload_id': chunked_upload.upload_id,
                'filename': chunked_upload.filename,
                'pk': self.pk}


def home(request):
    return render(request, 'GDapp/home.html')


def image_view(request):
    if request.method == 'POST':
        form = EMImageForm(request.POST, request.FILES)
        if form.is_valid():
            print('forms valid')
            obj = EMImage.objects.get(pk=form.cleaned_data['preloaded_pk'])
            obj.trained_model = form.cleaned_data['trained_model']
            obj.particle_groups = form.cleaned_data['particle_groups']
            obj.threshold_string = form.cleaned_data['threshold_string']
            obj.save()
            return run_gd(request, {'pk':obj.id})
    else:
        form = EMImageForm()
    return render(request, 'GDapp/upload.html', {'form': form})


def run_gd(request, inputs):
    pk = inputs['pk']
    gold_digger = GdappConfig.gold_particle_detector
    gold_digger(pk)
    return render(request, 'GDapp/run_gd.html', {'pk': pk})


# attempt to make a downloadable csv
def export(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
