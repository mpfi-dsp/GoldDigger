from celery import shared_task
from time import sleep
from celery_progress.backend import ProgressRecorder
from subprocess import run, PIPE
import sys

@shared_task(bind=True)
def gd_task(self, model):
    progress_recorder = ProgressRecorder(self)
    # for i in range(5):
    #     sleep(duration)
    progress_recorder.set_progress(0, 5)
    out = run([sys.executable, 'run.py', model], shell=False, stdout=PIPE)
    progress_recorder.set_progress(5,5)
    print(out)
    return 'Done'
