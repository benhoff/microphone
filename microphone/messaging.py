import zmq
from vexmessage import create_vex_message


class Messaging:
    def __init__(self,
                 publish_address: str,
                 subscribe_address: str,
                 audio_publish_address: str):

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

        self.publish_socket.connect(publish_address)
        self.subscribe_socket.connect(subscribe_address)
        self.audio_socket.connect(audio_publish_address)

    def send_response(self, target, **contents):
        frame = create_vex_message(target,
                                   'microphone',
                                   'RSP',
                                   **contents)

        self.publish_socket.send_multipart(frame)

    def send_audio(self, target, **contents):
        frame = create_vex_message(target,
                                   'microphone',
                                   'AUDIO',
                                   **contents)

        self.audio_socket.send_multipart(frame)
