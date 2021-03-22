import os
from django.db import models
from django import forms
from django.core.validators import MinValueValidator
from django.core.files import File
from chunked_upload.models import ChunkedUpload
import logging
import pathlib

logger = logging.getLogger(__name__)

TRAINED_MODEL_CHOICES = [
    ('43kGoldDigger', 'GoldDigger for small particles in 43k images'),
    ('87kGoldDigger', 'General GoldDigger')
]

MyChunkedUpload = ChunkedUpload
MyChunkedMaskUpload = ChunkedUpload

class EMImage(models.Model):
    image = models.FileField(upload_to="Input/", blank=True, default='')
    mask = models.FileField(upload_to="Mask/", blank=True)
    threshold_string = models.CharField(max_length=200, blank=True, default="1, 60",
                                        help_text="Input comma-separated values to serve as the upper and lower boundaries for the area of each particle size.")
    thresh_sens = models.FloatField(max_digits=10, decimal_places=10, default = 4.)
    local_image = models.FilePathField(path='/usr/src/local-images', blank=True)
    local_mask = models.FilePathField(path='/usr/src/local-images', blank=True)
    threshold_string = models.CharField(max_length=200, blank=True, default="1, 300")

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
    logger.debug("image saved: "+ f'image{pk}{ext}')


def add_histogram_image(pk, url):
    gd_data = EMImage.objects.get(pk=pk)
    temp_image = File(open(url, "rb"))
    _, ext = os.path.splitext(url)
    gd_data.histogram_image.save(f'histogram_{pk}{ext}', temp_image)
    logger.debug("histogram saved: "+ f'histogram_{pk}{ext}' )

def add_analyzed_image(pk, url):
    gd_data = EMImage.objects.get(pk=pk)
    temp_image = File(open(url, "rb"))
    _, ext = os.path.splitext(url)
    gd_data.analyzed_image.save(f'image_{pk}{ext}', temp_image)
    logger.debug("analyzed image saved: "+ f'image_{pk}{ext}')


def add_gold_particle_coordinates(pk, url):
    gd_data = EMImage.objects.get(pk=pk)
    temp_file = File(open(url, "rb"))
    gd_data.gold_particle_coordinates.save(f'coordinates_{pk}_.csv', temp_file)
    logger.debug("gold particle coordinates saved: "+ f'coordinates_{pk}_.csv')


def add_output_file(pk, url):
    gd_data = EMImage.objects.get(pk=pk)
    temp_file = File(open(url, "rb"))
    _, ext = os.path.splitext(url)
    print(f'image attribute: {gd_data.image}')
    print(f'local image attribute: {gd_data.local_image}')
    try:
        print(f'image attribute path: {gd_data.image.path}')
    except:
        print('COULD NOT PRINT IMAGE PATH')
    try:
        print(f'local image attribute path: {gd_data.local_image.path}')
    except:
        print('COULD NOT PRINT LOCAL IMAGE PATH')

    try:
        image_path = gd_data.image.path
        imageName = pathlib.Path(image_path).stem
        logger.debug("output imageName from image field")
    except:
        image_path = gd_data.local_image
        imageName = pathlib.Path(image_path).stem
        logger.debug("output imageName from local_image field")

    # if hasattr(gd_data, 'image') and hasattr(gd_data.image, 'url'):
    #     image_path = gd_data.image.path
    #     imageName = pathlib.Path(image_path).stem
    #     logger.debug("output imageName from image field")
    # elif hasattr(gd_data, 'local_image') and hasattr(gd_data.local_image, 'url'):
    #     image_path = gd_data.local_image.path
    #     imageName = pathlib.Path(image_path).stem
    #     logger.debug("output imageName from local_image field")
    # else:
    #     logger.debug("no image field found, unable to create output file")


    gd_data.output_file.save(f'Output_{imageName}{ext}', temp_file)
    logger.debug("output file saved: "+ f'Output_{imageName}{ext}')



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
