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