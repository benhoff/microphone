import zmq
from plugin_manager import AudioPluginManager


class Reactor(object):
    def __init__(self, context=None, **kwargs):
        context = context or zmq.Context()
        self.address_frontend = kwargs.get('address_frontend',
                                           'tcp://*:5556')

        self.address_backend = kwargs.get('address_backend',
                                          'inproc://microphone')

        # create the public facing communication socket
        self.frontend_communication = context.socket(zmq.ROUTER)
        self.frontend_communication.bind(self.address_frontend)

        # create internal communications
        self.backend_communication = context.socket(zmq.ROUTER)
        self.backend_communication.bind(self.address_backend)

    def run(self):
        pass

