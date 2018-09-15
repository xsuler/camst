from channels.generic.websocket import WebsocketConsumer
import campip.views
import json


class AlarmConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        global channel_name
        campip.views.channel_name = self.channel_name

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        print(text_data)

    def send_alarm(self, alarm):
        self.send(text_data=json.dumps({'info': alarm['info']}))
