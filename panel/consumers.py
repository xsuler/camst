from channels.generic.websocket import WebsocketConsumer
import json

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

        self.send(text_data=json.dumps({
            'message': 'asdadsd'
        }))

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        print(text_data)

