from GDapp.models import EMImage
from run import run_gold_digger
from GDapp.prediction.FrontEndUpdater import FrontEndUpdater
from celery import shared_task
import time


@shared_task(bind=True)
def celery_timer_task(self, pk):
    print(pk)
    feu = FrontEndUpdater(pk)
    time.sleep(5)
    feu.update(10,"update from celery timer task")
    return ('Done')

@shared_task(bind=True)
def run_gold_digger_task(self, pk):
    print(pk)
    obj = EMImage.objects.get(pk=pk)
    if obj.mask.name == '':
        mask = None
    else:
        mask = obj.mask.path
    front_end_updater = FrontEndUpdater(pk)
    # try:
    front_end_updater.update(0, "running gold digger")
    run_gold_digger(obj.trained_model, obj.image.path, obj.particle_groups, mask, front_end_updater)
    # except Exception as e:
        # front_end_updater.error_message(str(e))