from GDapp.prediction.FrontEndUpdater import FrontEndUpdater
from django.apps import AppConfig
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import time
import threading

channel_layer = get_channel_layer()

def slow_response_function():
    time.sleep(3)
    print('slow function done')
    send_a_message()

def send_a_message():
    pk = 152
    pk_group_name = "analysis_%s" % pk
    async_to_sync(channel_layer.group_send)(
        pk_group_name,
        {
            'type': 'analysis_message',
            'message': 'this is a delayed message from apps.py!'
        })

def update_front_end_test(pk):
    feu = FrontEndUpdater(pk)
    feu.post_message('Front End Updater Updating')

def test_slow_responder():
    x = threading.Thread(target=slow_response_function)
    x.start()

class GdappConfig(AppConfig):
    name = 'GDapp'
    gold_particle_detector = test_slow_responder