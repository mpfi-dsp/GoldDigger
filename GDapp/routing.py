from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/run_gd/(?P<pk>\w+)/$', consumers.AnalysisConsumer),
]
