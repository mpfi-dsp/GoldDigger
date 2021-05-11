from GDapp.tasks import check_if_celery_worker_active, save_to_queue, check_for_items_in_queue, start_tasks
from GDapp.prediction.FrontEndUpdater import FrontEndUpdater
from GDapp.apps import GdappConfig
from django.shortcuts import render, redirect
from .forms import EMImageForm, LocalFilesForm
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from django.views.generic.list import ListView
import csv
from django.http import HttpResponse
from .models import EMImage, MyChunkedUpload, MyChunkedMaskUpload
from chunked_upload.views import ChunkedUploadView, ChunkedUploadCompleteView
from django.views.generic import ListView
import os
import pathlib
from config import VERSION_NUMBER
import shutil

import sys
import logging

# logger settings
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(name)-12s %(levelname)-8s %(message)s'
        },
        'file': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
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
        },
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['console', 'file']
        },
        'django.utils.autoreload': {
            'level': 'INFO',
        },
        'daphne.http_protocol': {
            'level': 'INFO',
        },
        'django.db.backends': {
            'level': 'INFO',
        },
        'daphne.ws_protocol': {
            'level': 'INFO',
        },
        'django.channels.server': {
            'level': 'WARNING',
        },
        'aioredis': {
            'level': 'INFO',
        },
    }
})

logger = logging.getLogger(__name__)


class MyChunkedUploadView(ChunkedUploadView):
    '''Class for MyChunkedUploadView functions'''
    model = MyChunkedUpload
    field_name = 'the_file'
    def check_permissions(self, request):
        '''Allow non authenticated users to make uploads'''
        pass


class MyChunkedUploadCompleteView(ChunkedUploadCompleteView):
    '''Class for MyChunkedUploadCompleteView functions'''
    model = MyChunkedUpload
    def check_permissions(self, request):
        '''Allow non authenticated users to make uploads'''
        pass

    def on_completion(self, uploaded_file, request):
        '''This function saves the uploaded image file to an EMImage object'''
        instance = EMImage.objects.create(image=uploaded_file)
        self.pk = instance.id
        instance.save()


    def get_response_data(self, chunked_upload, request):
        '''This function prints information about the upload to the webpage'''
        return {'message': ("You successfully uploaded '%s' (%s bytes)!" %
                            (chunked_upload.filename, chunked_upload.offset)),
                'upload_id': chunked_upload.upload_id,
                'filename': chunked_upload.filename,
                'pk': self.pk}


class MyChunkedMaskUploadView(ChunkedUploadView):
    '''Class for MyChunkedMaskUploadView functions'''
    model = MyChunkedMaskUpload
    field_name = 'the_mask'
    def check_permissions(self, request):
        '''Allow non authenticated users to make uploads'''
        pass


class MyChunkedMaskUploadCompleteView(ChunkedUploadCompleteView):
    '''Class for MyChunkedMaskUploadCompleteView functions'''
    model = MyChunkedMaskUpload
    def check_permissions(self, request):
        '''Allow non authenticated users to make uploads'''
        pass
    def on_completion(self, uploaded_file, request):
        '''This function saves the uploaded mask file to an EMImage object'''
        obj = EMImage.objects.get(pk=request.POST['pk'])
        obj.mask = uploaded_file
        obj.save()

        print(request.POST)

    def get_response_data(self, chunked_upload, request):
        '''This function prints information about the upload to the webpage'''
        return {'message': ("You successfully uploaded '%s' (%s bytes)!" %
                            (chunked_upload.filename, chunked_upload.offset)),
                'upload_id': chunked_upload.upload_id,
                'filename': chunked_upload.filename}

class RunListView(ListView):
    '''creates previous runs page'''
    model = EMImage
    context_object_name = 'run_list'
    queryset = EMImage.objects.exclude(analyzed_image='').order_by('-id')
    template_name = 'runs.html'


class UnfinishedRunListView(ListView):
    '''creates unfinished runs page'''
    model = EMImage
    context_object_name = 'to_run_list'
    queryset = EMImage.objects.filter(analyzed_image='').order_by('-id')
    template_name = 'unfinished_runs.html'


def home(request):
    '''Homepage view, renders home.html file'''
    logger.debug("homepage accessed")
    return render(request, 'GDapp/home.html', {'version': VERSION_NUMBER})


def populate_em_obj(obj, form):
    '''
    This function returns cleaned data for parameters in an EMImage object
    Parameters:
        obj: EMImage object
        form: Completed upload form

    Returns:
        obj: EMImage object now with filled parameter fields
    '''
    obj.trained_model = form.cleaned_data['trained_model']
    obj.particle_groups = form.cleaned_data['particle_groups']
    obj.threshold_string = form.cleaned_data['threshold_string']
    obj.thresh_sens = form.cleaned_data['thresh_sens']
    return obj


def create_single_local_image_obj(form, local_files_form, image_path=None, mask_path=None):
    '''
    This function creates an EMImage object for 1 image, mask, and set of parameters.

    Parameters:
        form: EMImageForm object
        local_files_form: LocalFilesForm object
        image_path: Path to image file
        mask_path: Path to mask file

    Returns:
        obj: Filled EMImage object

    '''
    obj = form.save(commit=False)
    if image_path:
        obj.local_image = image_path
    else:
        obj.local_image = local_files_form.cleaned_data["local_image"]

    if mask_path is not None:
        obj.local_mask = mask_path
    else:
        try:
            obj.local_mask = local_files_form.cleaned_data["local_mask"]
        except:
            obj.local_mask = None
    obj = populate_em_obj(obj, form)
    obj.pk = None
    obj.id = None
    obj.save()
    return obj


def clean_mask(m):
    '''
        This function cleans the mask file name so it can be matched with image names.
        Parameters:
            m: Path to mask file
        Returns:
            m_clean: String containing only the stem of the mask file path with "mask" removed from the name
    '''
    m_stem = pathlib.Path(m).stem
    m_lower = m_stem.lower()
    m_nospace = m_lower.replace(" ", "")
    m_clean = m_nospace.replace('mask', '')
    return m_clean


def sort_masks_and_images(all_files, dir_path):
    '''
        This function adds image files to either a mask or image list depending on
        the filename.
        Parameters:
            all_files: list of files in the directory
            dir_path: path to the directory
        Returns:
            masks: List of files to be treated as masks (image filetype that contains "mask" in the filename)
            images: List of files to be treated as images (image filetype that does not contain "mask" in the filename)
    '''
    masks = []
    images = []
    for file in all_files:
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.tif')):
            if "mask" in file.lower():
                masks.append(os.path.join(dir_path, file))
            else:
                images.append(os.path.join(dir_path, file))
        else:
            logger.debug(f"not an image: {file}")

    return masks, images

def find_matching_mask(image, masks, dir_path):
    '''
        This function checks an image for a matching mask. A mask is matched
        with an image if the string outputted by clean_mask() is contained
        within the image name. This function ignores capitalization and spacing
        in the mask and image names.

        Parameters:
            image: Path to an image file.
            masks: List of mask files.
            dir_path: Path to uploaded directory.
        Returns:
            mask_path: Path to mask that matches the given image. Contains empty
                string if no such mask exists.

    '''

    mask_path = ''
    image_stem = pathlib.Path(image).stem
    image_lower = image_stem.lower()
    image_clean = image_lower.replace(" ", "")

    for m in masks:
        m_clean = clean_mask(m)
        if m_clean in image_clean:
            mask_path = os.path.join(dir_path, m)
            return mask_path
    return mask_path


def load_all_images_from_dir(form, local_files_form):
    '''
        This function creates an EMImage object for every (non-mask) image in a
        directory.

        Parameters:
            form: EMImageForm object
            local_files_form: LocalFilesForm object

        Returns:
            pk_list: List of pks for each EMImage object created

    '''
    dir_path = local_files_form.cleaned_data["local_image"]
    logger.debug(f"directory path: {dir_path}")
    all_files = os.listdir(dir_path)
    pk_list = []
    masks, images = sort_masks_and_images(all_files, dir_path)

    for f in images:
        file_path = os.path.join(dir_path, f)
        mask_path = find_matching_mask(f, masks, dir_path)
        obj = create_single_local_image_obj(form, local_files_form, image_path=file_path, mask_path=mask_path)
        log_obj(obj)
        pk_list.append(obj.id)

    return pk_list

def chunked_file_upload(form):
    '''
        This function creates an EMImage object for an image uploaded via chunked upload.

        Parameters:
            form: EMImageForm object
        Returns:
            obj: Filled EMImage Object
    '''
    obj = EMImage.objects.get(pk=form.cleaned_data['preloaded_pk'])
    obj = populate_em_obj(obj, form)
    obj.save()
    return obj


def image_view(request):
    '''
    This function generates the image upload page and creates EMImage objects
    from the submitted data.

    Parameters:
        request: 'POST' or 'GET'
    Returns:
        if request.method=='POST': Calls run_gd on list of pks for newly created EMImage objects
        if request.method=='GET': Displays image_upload webpage

    '''
    if request.method == 'POST':
        form = EMImageForm(request.POST, request.FILES)
        local_files_form = LocalFilesForm(request.POST)

        if form.is_valid() and local_files_form.is_valid() and not (local_files_form.cleaned_data["local_image"] == "" and form.cleaned_data["preloaded_pk"] == ""):
            if form.cleaned_data['preloaded_pk'] == '': # local file used
                pk_list = load_all_images_from_dir(form, local_files_form)
                return run_gd(request, {'pk': pk_list})

            else: # chunked file upload
                obj = chunked_file_upload(form)
            logger.debug("form valid, object saved")
            return run_gd(request, {'pk': obj.id})
    else:
        form = EMImageForm()
        local_files_form = LocalFilesForm()

    return render(request, 'GDapp/upload.html', {'form': form, 'local_files_form': local_files_form})


def run_gd(request, inputs):
    '''
    This function calls run_gold_digger_task for each item in a list

    Parameters:
        request: request object used to generate render response (for run_gd.html page)
        inputs: pk list or single pk for EMImage object(s)

    Returns:
        render of run_gd.html page (progress bar page) for the first object in the list.
    '''

    pk = inputs['pk']
    logger.debug(f"INSIDE run_gd FUNCTION FOR pk: {pk}")
    if not isinstance(pk, list):
        pk = [pk]

    fresh_start = not check_if_celery_worker_active()

    logger.debug(f"fresh_start: {fresh_start}")
    for pk_single in pk:
        save_to_queue(pk_single)
    if fresh_start:
        start_tasks()
    return render(request, 'GDapp/run_gd.html', {'pk': pk[0]})


def log_obj(obj):
    '''
    This function prints the (locally selected) EMImage object to the log file

    Parameters:
        obj: EMImage object
    '''
    logger.debug(f"local_image (path): {obj.local_image}")
    logger.debug(f"local_mask (path): {obj.local_mask}")
    logger.debug(f"trained_model: {obj.trained_model}")
    logger.debug(f"particle_groups: {obj.particle_groups}")
    logger.debug(f"threshold_string: {obj.threshold_string}")
    logger.debug(f"thres_sens: {obj.thresh_sens}")
    try:
        logger.debug(f"pk: {obj.id}") #always prints "None" ... why?
    except:
        logger.debug(f"could not print obj.id")


def clearQueue(request):
    '''
    '''
    logger.debug("INSIDE clearQueue FUNCTION")
    shutil.rmtree('../media/queue.pkl', ignore_errors=True)
    logger.debug("COMPLETED clearQUEUE FUNCTION")
    #return HttpResponse(request.POST['text'])
    return render(request, 'GDapp/upload.html')
