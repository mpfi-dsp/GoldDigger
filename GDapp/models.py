import os
from django.db import models
from django import forms
from django.core.validators import MinValueValidator
from django.core.files import File

TRAINED_MODEL_CHOICES = [
    ('43kGoldDigger', '43kGoldDigger'),
    ('87kGoldDigger', '87kGoldDigger')
]


class EMImage(models.Model):
    image = models.FileField(upload_to="Input/", blank=True, default='')
    mask = models.FileField(upload_to="Mask/", blank=True)
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

    #eleanor added coordinates6nm
    coordinates6nm = models.FileField(
            upload_to="analyzed/coordinates6nm", null=True)

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


def get_histogram_image_url(pk):
    gd_data = EMImage.objects.get(pk=pk)
    return gd_data.histogram_image.url


def get_analyzed_image_url(pk):
    gd_data = EMImage.objects.get(pk=pk)
    return gd_data.analyzed_image.url


def get_gold_particle_coordinates_url(pk):
    gd_data = EMImage.objects.get(pk=pk)
    return gd_data.gold_particle_coordinates.url

#eleanor added
def add_coordinates6nm(pk, url):
    gd_data = EMImage.objects.get(pk=pk)
    temp_file = File(open(url, "rb"))
    gd_data.coordinates6nm.save(f'coordinates6nm_{pk}_.csv', temp_file)

def get_coordinates6nm_url(pk):
    gd_data = EMImage.objects.get(pk=pk)
    return gd_data.coordinates6nm.url
