from GDapp.models import get_analyzed_image_url, get_histogram_image_url
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# from spineyolo.models import get_coordinates_url, get_analyzed_image_url

channel_layer = get_channel_layer()


class FrontEndUpdater:

    def __init__(self, pk):
        self.pk = pk
        self.total_count = 20
        self.latest_message = "Progress"

    def update(self, counter, message):
        self.post_message(message)
        self.update_progress(counter/10 * 100, 0)

    def update_progress(self, progress_percentage, progress_bar_index='0'):
        self.__send_progress(progress_percentage, progress_bar_index, self.latest_message)

    def post_message(self, message):
        self.latest_message = message
        self.__send_a_message(message)

    def analysis_done(self):
        self.update_progress(100)
        self.__send_a_message("Analysis Done")
        self.__send_finished()

    def error_message(self, message):
        self.__send_error_message(message)

    def __send_error_message(self, message):
        pk_group_name = "analysis_%s" % self.pk
        async_to_sync(channel_layer.group_send)(
            pk_group_name,
            {
                'type': 'error_message',
                'message': message
            })

    def __send_a_message(self, message):
        pk_group_name = "analysis_%s" % self.pk
        async_to_sync(channel_layer.group_send)(
            pk_group_name,
            {
                'type': 'analysis_message',
                'message': message
            })

    def __send_progress(self, progress, progress_bar_index, progress_message):
        pk_group_name = "analysis_%s" % self.pk
        async_to_sync(channel_layer.group_send)(
            pk_group_name,
            {
                'type': 'progress_percent',
                'progress': progress,
                'progress_bar_index': progress_bar_index,
                'progress_message': progress_message
            })

    def __send_finished(self):
        print("does this work even")
        pk_group_name = "analysis_%s" % self.pk
        # TODO: change this to get a personalized result based on pk
        gd_data = EMImage.objects.get(pk=pk)
        imageName = os.path.basename(gd_data.image.path())

        results_url = f"../../../media/Output_{imageName}.zip"
        analyzed_image_url = get_analyzed_image_url(self.pk)
        histogram_image_url = get_histogram_image_url(self.pk)
        async_to_sync(channel_layer.group_send)(
            pk_group_name,
            {
                'type': 'finished_message',
                'finished': "finished",
                'results_url': results_url,
                'analyzed_image_url': analyzed_image_url,
                'histogram_image_url': histogram_image_url,
            })
