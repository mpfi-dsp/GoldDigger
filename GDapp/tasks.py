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

@shared_task(bind=True)
def celery_timer_task(self, pk):
    print(pk)
    feu = FrontEndUpdater(pk)
    time.sleep(5)
    feu.update(10, f"Update from celery timer task {pk}")
    return ('Done')


@shared_task(bind=True)
def run_gold_digger_task(self, pk):
    print(pk)
    obj = EMImage.objects.get(pk=pk)
    mask_path = get_mask(obj)
    image_path = get_image(obj)

    front_end_updater = FrontEndUpdater(pk)

    front_end_updater.update(0, "running gold digger")
    run_gold_digger(obj.trained_model, image_path, obj.particle_groups,
                    obj.threshold_string, thresh_sens=obj.thresh_sens, mask=mask_path, front_end_updater=front_end_updater)
    return ('Done')

@shared_task(bind=True)
def after_task(self):
    start_tasks()

def start_tasks():
    pk = pop_pk_from_queue()
    if pk is not None:
        gd_task = run_gold_digger_task.si(pk)
        gd_task.link(after_task.si())
        gd_task.delay()


def get_mask(obj):
    if obj.mask.name == "" and obj.local_mask == "" :
        mask = None
    elif obj.mask.name == "":
        mask = obj.local_mask
    else:
        mask = obj.mask.path
    return mask


def get_image(obj):
    if obj.image.name == "":
        return obj.local_image
    else:
        return obj.image.path

def check_for_items_in_queue():
    queue_path = 'media/queue.pkl'
    if os.path.exists(queue_path):
        with open(queue_path, 'rb') as queue_save_file:
            pk_queue = pickle.load(queue_save_file)
        if pk_queue:
            logger.debug("LOGGER: items in queue TRUE")
            print("items in queue TRUE")
            return True
    else:
        logger.debug("LOGGER: items in queue FALSE")
        print("items in queue FALSE")
        return False

def check_if_celery_worker_active():
    for key, val in celery_app.control.inspect().active().items():
        dict_is_empty = len(val)==0
        print(f"value is zero? {len(val)==0}")
    if dict_is_empty:
        print("Celery Inactive")
        return False
    else:
        print("Celery Active")
        return True

def save_to_queue(pk):
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
