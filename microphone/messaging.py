import zmq

from vexmessage import create_vex_message, decode_vex_message


class Messaging:
    def __init__(self, settings):
        context = zmq.Context()
        # Pub/Sub sockets communicate on the vexbot node
        self.publish_socket = context.socket(zmq.PUB)
        self.subscribe_socket = context.socket(zmq.SUB)
        # TODO: Subscribe to random string? Something more descriptive
        self.subscribe_socket.setsockopt_string(zmq.SUBSCRIBE, '')
        self.audio_socket = context.socket(zmq.PUB)

        # audio socket should connect to the speech recongnition node
        # TODO: If I have multiple devices recording simulatenously
        # how am I going to handle that?

        publish_address = settings.get('publish_address')
        subscribe_address = settings.get('subscribe_address')
        audio_publish_address = settings.get('audio_publish_address')

        self.publish_socket.connect(publish_address)
        self.subscribe_socket.connect(subscribe_address)
        self.audio_socket.connect(audio_publish_address)
