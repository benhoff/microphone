import argparse

from threading import Thread
import zmq
from plugin_manager import AudioPluginManager


class MetadriverCMD:
    list = 'list'
    active = 'active'


class CommunicationNode(object):
    def __init__(self, context=None, **kwargs):
        self._context = context or zmq.Context()
        self.address_frontend = kwargs.get('address_frontend',
                                           'tcp://localhost:5556')

        # this might need to be defaulted to a tcp device?
        self.address_backend = kwargs.get('address_backend',
                                          'inproc://microphone')

        # create the public facing communication socket
        self.frontend_communication = self._context.socket(zmq.ROUTER)
        self.frontend_communication.bind(self.address_frontend)

        # create internal communications
        self.backend_communication = self._context.socket(zmq.DEALER)
        self.backend_communication.bind(self.address_backend)
        self.plugin_manager = AudioPluginManager()


    def run(self):
        frontend = self.frontend_communication
        while True:
            frame = frontend.recv_multipart()
            frame.pop(0)            # id
            cmd_type = frame.pop(0)
            arg = frame.pop()       # optional arg
            cmd = frame.pop()       # cmd
            # NOTE: metadriver commands do NOT have a name attr
            name = None
            if not cmd_type == b'metadriver':
                name = frame.pop()  # name, either driver name or instance id
            if cmd_type == b'instance' or cmd_type == b'driver':
                # FIXME: pretty sure the first part needs to be an socket id
                self.backend_communication.send_multipart((name,
                                                           cmd_type,
                                                           cmd,
                                                           arg))

            elif cmd_type == b'metadriver':
                pass


    def invoke_driver(self, driver):
        """
        driver's manage multiple devices
        """
        driver = self.plugin_manager.get_plugins(_get_driver(driver))
        self.plugin_manager.add_plugins(driver())
        self.frontend_communication.send_multipart([b"driver", b"invoked"])


def _get_driver(name):
    def filter_function(plugins):
        for plugin in plugins:
            if plugin.__name__ == name:
                return plugin

    return filter_function

def main(*args):
    communication_node = CommunicationNode()



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--frontend_adress', store=True, default='tcp://localhost:5561')
    parser.add_argument('--backend_address', store=True, default='tcp://localhost:5562')
    args = parser.parse_args()
    main(args)
    pass
