import os
from django.db import models
from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.files import File
from chunked_upload.models import ChunkedUpload
import logging
import pathlib

# gets logger config info (specified in views.py)
logger = logging.getLogger(__name__)

# ('model name within code', 'model display name')
# add to this list if adding a new trained model
TRAINED_MODEL_CHOICES = [
    ('43kGoldDigger', 'GoldDigger for small particles in 43k images'),
    ('87kGoldDigger', 'General GoldDigger (87k)'),
    #('032521Experimental', '03/25/2021 Experimental GoldDigger'),
    ('greenonly_041421', 'Green Only GoldDigger (04/14/2021)'),
    ('balanced_041421', 'Balanced GoldDigger (04/14/2021)')
]

MyChunkedUpload = ChunkedUpload
MyChunkedMaskUpload = ChunkedUpload


class EMImage(models.Model):
    '''
        This class stores parameters and output for one image.

        Attributes:
            image (FileField): The image chosen for chunked upload (accomodates 1 file at a time)
            mask (FileField): The mask chosen for chunked upload (optional)
            threshold_string (CharField): Upper and lower boundaries for each particle size. Input 2, 4, or 6 comma separated values for 1, 2, or 3 particle groups.
            thresh_sens (FloatField): Accepts integer or float values for threshold sensitivity. Default value is 4. Affects how sensitive the floodfill for particle area is to changes in color.
            local_image (FilePathField): Contains the path to an image in the Docker container in /usr/src/local-images. Used for local file upload. This field will only exist if there is nothing in the "image" field.
            local_mask (FilePathField): Contains the path to an mask in the Docker container in /usr/src/local-images. Used for local file upload. Optional. This field will only exist if there is nothing in the "mask" field.
            particle_groups (IntegerField): Accepts integers 1, 2 or 3. Determines how many categories the gold particles will be sorted into based on the area boundaries provided by threshold_string.
            trained_model (CharField): Allows trained model choices from the TRAINED_MODEL_CHOICES list. Determines which network will be used to analyze the image.
            gold_particle_coordinates (FileField): CSV file of all x,y gold particle coordinates found along with their areas. This file is presented as a download link on the "Previous Runs" tab.
            analyzed_image (ImageField): Output image created by Gold Digger network (OutputStitched.png with particle coordinates plotted)
            histogram_image (ImageField): Histogram of gold particle areas.
            output_file (FileField): .zip file containing output from GoldDigger (coordinates file, Cropped image, histogram, etc).
            chunked_image_id (CharField): NEVER USED???
            chunked_mask_id (CharField): NEVER USED???
            chunked_image_linked (ForeignKey): NEVER USED???
            preloaded_pk (CharField): Unique ID for the object (automatically generated and assigned).
            created_at (DateTimeField): Date and time the object was created (in UTC).

    '''

    image = models.FileField(upload_to="Input/", blank=True, default='')
    mask = models.FileField(upload_to="Mask/", blank=True)
    threshold_string = models.CharField(max_length=200, blank=True, default="1, 60",
                                        help_text="Input comma-separated values to serve as the lower and upper boundaries for the area of each particle size.")
    thresh_sens = models.FloatField(default = 4.)

    # path for local_mask and local_images references location in the docker container, these are for local upload
    local_image = models.FilePathField(path='/usr/src/local-images', blank=True)
    local_mask = models.FilePathField(path='/usr/src/local-images', blank=True, default = '')

    particle_groups = models.IntegerField(
        blank=False, default=1, validators=[MinValueValidator(1), MaxValueValidator(3)])
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

def add_histogram_image(pk, url):
    '''
        This function saves a histogram of gold particle sizes to media/analyzed/histograms.
        Parameters:
        pk: preloaded_pk for EMImage object/front_end_updater.
        url: File path to where the histogram generated during run.py is saved.

    '''

    gd_data = EMImage.objects.get(pk=pk)
    temp_image = File(open(url, "rb"))
    _, ext = os.path.splitext(url)
    gd_data.histogram_image.save(f'histogram_{pk}{ext}', temp_image)
    logger.debug("histogram saved: "+ f'histogram_{pk}{ext}' )

def add_analyzed_image(pk, url):
    '''
        This function saves analyzed image (Gold Digger network output) to media/analyzed/images.
        Parameters:
        pk: preloaded_pk for EMImage object/front_end_updater.
        url: File path to where the analyzed image generated during run.py is saved.

    '''

    gd_data = EMImage.objects.get(pk=pk)
    temp_image = File(open(url, "rb"))
    _, ext = os.path.splitext(url)
    gd_data.analyzed_image.save(f'image_{pk}{ext}', temp_image)
    logger.debug("analyzed image saved: "+ f'image_{pk}{ext}')

def add_gold_particle_coordinates(pk, url):
    '''
        This function saves the csv of gold particle coordinates with their areas to media/analyzed/coordinates.
        Parameters:
        pk: preloaded_pk for EMImage object/front_end_updater.
        url: File path to where the coordinates file (all sizes) generated during run.py is saved.

    '''

    gd_data = EMImage.objects.get(pk=pk)
    temp_file = File(open(url, "rb"))
    gd_data.gold_particle_coordinates.save(f'coordinates_{pk}_.csv', temp_file)
    logger.debug("gold particle coordinates saved: "+ f'coordinates_{pk}_.csv')

def add_output_file(pk, url):
    '''
        This function saves the output zip file to media.
        Parameters:
        pk: preloaded_pk for EMImage object/front_end_updater.
        url: File path to where zip file generated during run.py is saved.

    '''

    gd_data = EMImage.objects.get(pk=pk)
    temp_file = File(open(url, "rb"))
    _, ext = os.path.splitext(url)
    print(f'image attribute: {gd_data.image}')
    print(f'local image attribute: {gd_data.local_image}')

    try:
        image_path = gd_data.image.path
        imageName = pathlib.Path(image_path).stem
        logger.debug("output imageName from image field")
    except:
        image_path = gd_data.local_image
        imageName = pathlib.Path(image_path).stem
        logger.debug("output imageName from local_image field")

    model = gd_data.trained_model
    gd_data.output_file.save(f'Output-{imageName}-with-{model}{ext}', temp_file)
    logger.debug("output file saved: "+ f'Output-{imageName}-with-{model}{ext}')

def get_histogram_image_url(pk):
    '''
        This function is used to help display the results of a single run.
        Parameters:
        pk: preloaded_pk for EMImage object/front_end_updater.
        Returns:
        gd_data.histogram_image.url: Location where histogram_image is saved for the EMImage object with a specified pk.

    '''

    gd_data = EMImage.objects.get(pk=pk)
    return gd_data.histogram_image.url

def get_analyzed_image_url(pk):
    '''
        This function is used to help display the results of a single run.
        Parameters:
        pk: preloaded_pk for EMImage object/front_end_updater.
        Returns:
        gd_data.analyzed_image.url: Location where analyzed_image is saved for the EMImage object with a specified pk.

    '''

    gd_data = EMImage.objects.get(pk=pk)
    return gd_data.analyzed_image.url
