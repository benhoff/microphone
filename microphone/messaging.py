import zmq

from vexmessage import create_vex_message, decode_vex_message


class Messaging:
    def __init__(self, settings):
        self.plugin = plugin
        context = zmq.Context()
        # Pub/Sub sockets communicate on the vexbot node
        self.publish_socket = context.socket(zmq.PUB)
        self.subscribe_socket = context.socket(zmq.SUB)
        # audio socket should connect to the speech recongnition node
        self.audio_socket = context.socket(zmq.PUB)
        # TODO: If I have multiple devices recording simulatenously
        # how am I going to handle that?

        # Is this needed?
        """
        self.communication_socket = context.socket(zmq.REQ)

        self.communication_socket.connect(backend_address)
        self.communication_socket.setsockopt_string(zmq.IDENTITY,
                                                    'pyaudioengine')

        self.communication_socket.send(b'READY')
        """
        publish_address = settings.get('publish_address')
        subscribe_address = settings.get('subscribe_address')
        audio_publish_address = settings.get('audio_publish_address')
