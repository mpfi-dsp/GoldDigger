from celery import shared_task
from time import sleep
from celery_progress.backend import ProgressRecorder
from subprocess import run, PIPE
import sys
from run import run_gold_digger
@shared_task(bind=True)
def gd_task(self, model):
    progress_recorder = ProgressRecorder(self)
    # out = run([sys.executable, 'run.py', model], shell=False, stdout=PIPE)
    run_gold_digger(model, progress_recorder)
    return 'Done'
