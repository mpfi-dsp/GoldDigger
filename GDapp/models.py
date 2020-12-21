import os
from django.db import models
from django import forms
from django.core.validators import MinValueValidator
from django.core.files import File
from chunked_upload.models import ChunkedUpload

TRAINED_MODEL_CHOICES = [
    ('43kGoldDigger', '43kGoldDigger'),
    ('87kGoldDigger', '87kGoldDigger')
]

MyChunkedUpload = ChunkedUpload
MyChunkedMaskUpload = ChunkedUpload

class EMImage(models.Model):
    image = models.FileField(upload_to="Input/", blank=True, default='')
    mask = models.FileField(upload_to="Mask/", blank=True)
    threshold_string = models.CharField(max_length=200, blank=True, initial="1, 300")

    particle_groups = models.IntegerField(
        blank=False, default=1, validators=[MinValueValidator(1)])
    trained_model = models.CharField(max_length=100,
                                     blank=False,
                                     default='87kGoldDigger',
                                     choices=TRAINED_MODEL_CHOICES)
    gold_particle_coordinates = models.FileField(
        upload_to="analyzed/coordinates", null=True)
    analyzed_image = models.ImageField(
        upload_to="analyzed/images", null=True)
    histogram_image = models.ImageField(
        upload_to="analyzed/histograms", null=True)


    output_file = models.FileField(
        upload_to="analyzed/output", null=True)
    #eleanor added coordinates
    #coordinatesGroup1 = models.FileField(
    #        upload_to="analyzed/coordinatesGroup1", null=True)

    chunked_image_id = models.CharField(max_length=500, blank=True, default="")
    chunked_mask_id = models.CharField(max_length=500, blank=True, default="")
    chunked_image_linked = models.ForeignKey(MyChunkedUpload, null=True, on_delete=models.CASCADE)
    preloaded_pk = models.CharField(max_length=10, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

def add_image(pk, url):
    gd_data = EMImage.objects.get(pk=pk)
    temp_image = File(open(url, "rb"))
    _, ext = os.path.splitext(url)
    gd_data.image.save(f'image{pk}{ext}', temp_image)

def add_histogram_image(pk, url):
    gd_data = EMImage.objects.get(pk=pk)
    temp_image = File(open(url, "rb"))
    _, ext = os.path.splitext(url)
    gd_data.histogram_image.save(f'histogram_{pk}{ext}', temp_image)

def add_analyzed_image(pk, url):
    gd_data = EMImage.objects.get(pk=pk)
    temp_image = File(open(url, "rb"))
    _, ext = os.path.splitext(url)
    gd_data.analyzed_image.save(f'image_{pk}{ext}', temp_image)


def add_gold_particle_coordinates(pk, url):
    gd_data = EMImage.objects.get(pk=pk)
    temp_file = File(open(url, "rb"))
    gd_data.gold_particle_coordinates.save(f'coordinates_{pk}_.csv', temp_file)


def add_output_file(pk, url):
    gd_data = EMImage.objects.get(pk=pk)
    temp_file = File(open(url, "rb"))
    _, ext = os.path.splitext(url)
    gd_data.output_file.save(f'output_{pk}{ext}', temp_file)



def get_histogram_image_url(pk):
    gd_data = EMImage.objects.get(pk=pk)
    return gd_data.histogram_image.url


def get_analyzed_image_url(pk):
    gd_data = EMImage.objects.get(pk=pk)
    return gd_data.analyzed_image.url


def get_gold_particle_coordinates_url(pk):
    gd_data = EMImage.objects.get(pk=pk)
    return gd_data.gold_particle_coordinates.url


def get_output_file_url(pk):
    gd_data = EMImage.objects.get(pk=pk)
    return gd_data.output_file.url

#eleanor added
#def add_coordinatesGroup1(pk, url):
#    gd_data = EMImage.objects.get(pk=pk)
#    temp_file = File(open(url, "rb"))
#    gd_data.coordinatesGroup1.save(f'coordinatesGroup1_{pk}_.csv', temp_file)

#def get_coordinatesGroup1_url(pk):
#    gd_data = EMImage.objects.get(pk=pk)
#    return gd_data.coordinatesGroup1.url
