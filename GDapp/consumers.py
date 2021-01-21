from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

class AnalysisConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.pk = self.scope['url_route']['kwargs']['pk']
        self.pk_group_name = "analysis_%s" % self.pk

        # Join room group
        await self.channel_layer.group_add(
            self.pk_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.pk_group_name,
            self.channel_name
        )

    async def receive_json(self, content):
        json_type = content.get("type", None)
        print("content: ", content)
        print("msg_type: {}".format(json_type))
        # try:
        if json_type == "analysis_message":
            await self.send_message(content['message'])
        elif json_type == "progress_percent":
            await self.send_progress(content['progress'], content['progress_bar_index'], content['progress_message'])
        elif json_type == "finished":
            await self.send_progress(content['finished'])


    async def send_progress(self, progress, progress_bar_index, progress_message):

        await self.channel_layer.group_send(
            self.pk_group_name,
            {
                'type': 'progress_percent',
                'progress': progress,
                'progress_bar_index': progress_bar_index,
                'progress_message': progress_message,
            }
        )

    async def send_message(self, message):

        await self.channel_layer.group_send(
            self.pk_group_name,
            {
                'type': 'analysis_message',
                'message': message
            }
        )

    async def send_finished(self, message):

        await self.channel_layer.group_send(
            self.pk_group_name,
            {
                'type': 'finished_message',
                'finished': message
            }
        )

    async def progress_percent(self, event):
        progress = event['progress']
        progress_bar_index = event['progress_bar_index']
        progress_message = event['progress_message']
        # send progress to websocket
        await self.send_json({
            'progress': progress,
            'progress_bar_index':progress_bar_index,
            'progress_message': progress_message,
        })

    # receive message from pk group
    async def analysis_message(self, event):
        message = event['message']

        # send message to websocket
        await self.send_json({
            'message': message
        })

    # receive message from pk group
    async def error_message(self, event):
        message = event['message']
        # send message to websocket
        await self.send_json({
            'error': message,
        })

    # receive message from pk group
    async def finished_message(self, event):
        message = event['finished']
        results_url = event['results_url']
        analyzed_image_url = event['analyzed_image_url']
        histogram_image_url = event['histogram_image_url']

        # send message to websocket
        await self.send_json({
            'finished': message,
            'results_url': results_url,
            'analyzed_image_url':analyzed_image_url,
            'histogram_image_url':histogram_image_url
        })
