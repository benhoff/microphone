import zmq


class AudioNode(object):
    def __init__(self, context=None, **kwargs):
        context = context or zmq.Context()
        self.address_frontend = kwargs.get('address_frontend',
                                           'tcp://localhost:5555')

        self.address_backend = kwargs.get('address_backend',
                                          'inproc://microphone-audio')

        # create the public facing publish socket
        self.frontend_audio = context.socket(zmq.XPUB)
        self.frontend_audio.bind(self.address_frontend)
        # create the internal subscription endpoint
        self.backend_audio = context.socket(zmq.XSUB)
        self.backend_audio.bind(self.address_backend)

        # forward all audio internal traffic out
        zmq.proxy(self.backend_audio, self.frontend_audio)
