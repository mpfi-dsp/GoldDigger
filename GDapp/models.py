import os
from django.db import models
from django import forms
from django.core.validators import MinValueValidator
from django.core.files import File
from chunked_upload.models import ChunkedUpload
import logging


logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggets': False,
    'formatters': {
        'console': {
            'format': '%(name) -12s %(levelname) -8s %(message)s'
        },
        'file': {
            'format': '%(asctime)s %(name) -12s %(levelname) -8s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'file',
            'filename': '/tmp/debug.log'
        }
    },
    'loggers': {
        '':{
            'level': 'DEBUG',
            'handlers': ['console', 'file']
        }
    }

})

logger = logging.getLogger(__name__)

TRAINED_MODEL_CHOICES = [
    ('43kGoldDigger', '43kGoldDigger'),
    ('87kGoldDigger', '87kGoldDigger')
]

MyChunkedUpload = ChunkedUpload
MyChunkedMaskUpload = ChunkedUpload

class EMImage(models.Model):
    image = models.FileField(upload_to="Input/", blank=True, default='')
    mask = models.FileField(upload_to="Mask/", blank=True)
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
    logger.info("image saved: "+ f'image{pk}{ext}')


def add_histogram_image(pk, url):
    gd_data = EMImage.objects.get(pk=pk)
    temp_image = File(open(url, "rb"))
    _, ext = os.path.splitext(url)
    gd_data.histogram_image.save(f'histogram_{pk}{ext}', temp_image)
    logger.info("histogram saved: "+ f'histogram_{pk}{ext}' )

def add_analyzed_image(pk, url):
    gd_data = EMImage.objects.get(pk=pk)
    temp_image = File(open(url, "rb"))
    _, ext = os.path.splitext(url)
    gd_data.analyzed_image.save(f'image_{pk}{ext}', temp_image)
    logger.info("analyzed image saved: "+ f'image_{pk}{ext}')


def add_gold_particle_coordinates(pk, url):
    gd_data = EMImage.objects.get(pk=pk)
    temp_file = File(open(url, "rb"))
    gd_data.gold_particle_coordinates.save(f'coordinates_{pk}_.csv', temp_file)
    logger.info("gold particle coordinates saved: "+ f'coordinates_{pk}_.csv')


def add_output_file(pk, url):
    gd_data = EMImage.objects.get(pk=pk)
    temp_file = File(open(url, "rb"))
    _, ext = os.path.splitext(url)
    gd_data.output_file.save(f'output_{pk}{ext}', temp_file)
    logger.info("output file saved: "+ f'output_{pk}{ext}')



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
