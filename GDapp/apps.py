# from run import run_gold_digger
from GDapp.tasks import celery_timer_task, run_gold_digger_task
from GDapp.prediction.FrontEndUpdater import FrontEndUpdater
from django.apps import AppConfig
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import time
import threading

channel_layer = get_channel_layer()

# def slow_response_function(pk):
#     time.sleep(3)
#     print('slow function done')
#     send_a_message(pk)
#     send_a_message(pk,'second message')

# def celery_function(pk):
#     print(pk)
#     celery_timer_task.delay(pk)


# def send_a_message(pk=None, message=None):
#     if pk is None:
#         pk = 158
#     if message is None:
#         message = 'this is a delayed message from apps.py!'
#     pk_group_name = "analysis_%s" % pk
#     async_to_sync(channel_layer.group_send)(
#         pk_group_name,
#         {
#             'type': 'analysis_message',
#             'message': message
#         })

# def update_front_end_test(pk):
#     feu = FrontEndUpdater(pk)
#     feu.post_message('Front End Updater Updating')

# def test_slow_responder(pk):
#     x = threading.Thread(target=slow_response_function, args=[pk])
#     x.start()

class GdappConfig(AppConfig):
    name = 'GDapp'
    # gold_particle_detector = run_gold_digger
    # gold_particle_detector = celery_function
    gold_particle_detector = run_gold_digger_task.delay
