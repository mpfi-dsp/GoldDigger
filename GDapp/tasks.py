from GDapp.models import EMImage
from run import run_gold_digger
from GDapp.prediction.FrontEndUpdater import FrontEndUpdater
from celery import shared_task
import time


@shared_task(bind=True)
def celery_timer_task(self, pk):
    print(pk)
    feu = FrontEndUpdater(pk)
    time.sleep(2)
    feu.update(10, "update from celery timer task")
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
