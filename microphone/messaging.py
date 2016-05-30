import zmq

from vexmessage import create_vex_message, decode_vex_message


class Messaging:
    def __init__(self, settings):
        self.plugin = plugin
        self._context = zmq.Context()
        self.communication_socket = self._context.socket(zmq.REQ)

        self.communication_socket.connect(backend_address)
        self.communication_socket.setsockopt_string(zmq.IDENTITY,
                                                    'pyaudioengine')

        self.communication_socket.send(b'READY')

        self.publish = self._context.socket(zmq.PUB)
        self.audio_socket.connect(kwargs['audio_subscription_address'])
