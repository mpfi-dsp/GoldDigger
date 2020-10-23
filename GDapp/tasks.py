from celery import shared_task
from time import sleep
from celery_progress.backend import ProgressRecorder
from subprocess import run, PIPE
import sys
from run import run_gold_digger
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task(bind=True)
def gd_task(self, model, image, mask):
    progress_recorder = ProgressRecorder(self)
    # out = run([sys.executable, 'run.py', model], shell=False, stdout=PIPE)
    print(f'\nmodel: {model}, image: {image}\n')
    run_gold_digger(model, image, mask, progress_recorder)
    return 'Done'
