import zmq


class PluginMessaging:
    def __init__(self, plugin, backend_address, context=None, **kwargs):
        self.plugin = plugin
        self._context = context or zmq.Context()
        self.communication_socket = self._context.socket(zmq.REQ)

        self.communication_socket.connect(backend_address)
        self.communication_socket.setsockopt_string(zmq.IDENTITY,
                                                    'pyaudioengine')

        self.communication_socket.send(b'READY')

        self.audio_socket = self._context.socket(zmq.PUB)
        self.audio_socket.connect(kwargs['audio_subscription_address'])

    def send_multipart(self, msg):
        msg[0] = str(msg[0]).encode('ascii')
        msg[1] = bytes([msg[0]])
        self.audio_socket.send_multipart(msg)

    def run(self):
        while True:
            # NOTE: `frame` is a list of byte strings
            # Once we recv here, MUST reply in order to loop again!
            try:
                frame = self.communication_socket.recv_multipart()
            except KeyboardInterrupt:
                break

            # NOTE: pretty sure there will be two id's
            # 1st id, should be the request socket, and the second should be
            # the dealer

            command = frame.pop(0)
            optional_arg = frame.pop(0)

            if command == b'list_devices':
                devices = self.plugin.get_devices()
                # get out all the names and encode them in ascii to send
                devices = [x.encode('ascii') for x in devices.keys()]
                self.communication_socket.send_multipart(devices)
            elif command == b'record':
                device = self.plugin.devices[optional_arg.decode('utf-8')]
                print('recording!', optional_arg)
                bits = 16
                channels  = 2
                chunksize = 1024
                device.record(chunksize, bits, channels)
                self.communication_socket.send(b'')
            elif command == b'':
                self.communication_socket.send(b'')
            else:
                print('WARNING DID NOT PARSE PACKET IN PYAUDIO CORRECTLY, SENDING BLANK')
                self.communication_socket.send(b'')
