from GDapp.tasks import celery_timer_task, run_gold_digger_task
from GDapp.prediction.FrontEndUpdater import FrontEndUpdater
from django.apps import AppConfig
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import time
import threading

channel_layer = get_channel_layer()

class GdappConfig(AppConfig):
    name = 'GDapp'
    gold_particle_detector = run_gold_digger_task.delay
