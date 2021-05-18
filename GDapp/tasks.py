import logging
from GDapp.models import EMImage
from run import run_gold_digger
from GDapp.prediction.FrontEndUpdater import FrontEndUpdater
from celery import shared_task
from GoldDigger.celery import app as celery_app
import time
import collections, pickle
import os

logger = logging.getLogger(__name__)

# @shared_task(bind=True)
# def celery_timer_task(self, pk):
#     '''??? NEVER USED'''
#     print(pk)
#     feu = FrontEndUpdater(pk)
#     time.sleep(5)
#     feu.update(10, f"Update from celery timer task {pk}")
#     return ('Done')


@shared_task(bind=True)
def run_gold_digger_task(self, pk):
    '''
        This function calls run_gold_digger from run.py on an EMImage object

        Parameters:
            pk: pk for an EMImage object

        Returns "Done" when complete.

    '''
    print(pk)
    obj = EMImage.objects.get(pk=pk)
    mask_path = get_mask(obj)
    image_path = get_image(obj)

    front_end_updater = FrontEndUpdater(pk)

    front_end_updater.update(0, "running gold digger")
    obj.status = "Running Gold Digger"
    obj.save()

    run_gold_digger(obj.trained_model, image_path, obj.particle_groups,
                    obj.threshold_string, thresh_sens=obj.thresh_sens, mask=mask_path, front_end_updater=front_end_updater)
    #run_gold_digger(image_path, obj, mask=mask_path, front_end_updater=front_end_updater)

    #obj.status = "Completed Run"
    #obj.save()
    return ('Done')

@shared_task(bind=True)
def after_task(self):
    '''This function starts running the next EMImage object'''
    start_tasks()

def start_tasks():
    '''This function starts running queued EMImage objects by accessing their
    pks from the queue file'''
    pk = pop_pk_from_queue()
    if pk is not None:
        gd_task = run_gold_digger_task.si(pk)
        gd_task.link(after_task.si())
        gd_task.delay()


def get_mask(obj):
    '''
        This function returns the mask in the EMImage object depending on the upload method

        Parameters:
            obj: EMImage object

        Returns:
            mask: path to mask file
    '''
    if obj.mask.name == "" and obj.local_mask == "" :
        mask = None
    elif obj.mask.name == "":
        mask = obj.local_mask
    else:
        mask = obj.mask.path
    return mask


def get_image(obj):
    '''
        This function returns the image in the EMImage object depeding on the upload
        method

        Parameters:
            obj: EMImage object

        Returns:
            mask: path to mask file
    '''
    if obj.image.name == "":
        return obj.local_image
    else:
        return obj.image.path

def check_for_items_in_queue():
    '''
        This function returns True if there are items in the queue.pkl file and
        returns False otherwise
    '''
    queue_path = 'media/queue.pkl'
    if os.path.exists(queue_path):
        with open(queue_path, 'rb') as queue_save_file:
            pk_queue = pickle.load(queue_save_file)
        if pk_queue:
            logger.debug("LOGGER: items in queue TRUE")
            #print("items in queue TRUE")
            return True
        else:
            logger.debug("items in queue FALSE")
            return False
    else:
        logger.debug(f"{queue_path} does not exist")
        return False

def check_if_celery_worker_active():
    '''
        This function returns True if the celery worker for the queue is active
        and returns false otherwise.
    '''
    for key, val in celery_app.control.inspect().active().items():
        dict_is_empty = len(val)==0
        #print(f"value is zero? {len(val)==0}")
    if dict_is_empty:
        #print("Celery Inactive")
        return False
    else:
        #print("Celery Active")
        return True

def save_to_queue(pk):
    '''
        This function adds an EMImage object's pk to the queue of objects to be run

        Parameters:
            pk: pk/ID number of an EMImage object
    '''
    if os.path.isfile('media/queue.pkl'):
        with open('media/queue.pkl', 'rb') as queue_save_file:
            pk_queue = pickle.load(queue_save_file)
            pk_queue.append(pk)
    else:
        pk_queue = collections.deque()
        pk_queue.append(pk)
    with open('media/queue.pkl', 'wb+') as queue_save_file:
        pickle.dump(pk_queue, queue_save_file)


def pop_pk_from_queue():
    '''
        This function takes the next pk from the queue. This will always be the
        pk that was added earliest.

        Returns:
            pk: pk of EMImage object
            OR None if there are no items in the queue.
    '''
    if os.path.isfile('media/queue.pkl'):
        with open('media/queue.pkl', 'rb') as queue_save_file:
            pk_queue = pickle.load(queue_save_file)
            if pk_queue:
                pk = pk_queue.popleft()
                with open('media/queue.pkl', 'wb+') as queue_save_file:
                    pickle.dump(pk_queue, queue_save_file)
                return pk
            else:
                return None
    else: return None
