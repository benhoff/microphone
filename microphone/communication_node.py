import argparse
from subprocess import Popen
from threading import Thread

import zmq
from plugin_manager import AudioPluginManager

# FIXME
from audioengines.pyaudio_ae.pyaudio_ae import PyAudioEnginePlugin


class MetadriverCMD:
    list = 'list'
    active = 'active'


class CommunicationNode(object):
    def __init__(self, context=None, **kwargs):
        self._context = context or zmq.Context()
        self.frontend_adress = kwargs.get('frontend_adress',
                                           'tcp://127.0.0.1:5561')

        # this might need to be defaulted to a tcp device?
        self.backend_adress = kwargs.get('backend_adress',
                                         'tcp://127.0.0.1:5562')

        asa = kwargs.get('audio_subscription_address',
                         'tcp://127.0.0.1:5655')

        self.audio_subscription_address = asa
        # create the public facing communication socket
        self.frontend_communication = self._context.socket(zmq.ROUTER)
        self.frontend_communication.bind(self.frontend_adress)

        # create internal communications
        self.backend_communication = self._context.socket(zmq.DEALER)
        self.backend_communication.bind(self.backend_adress)

        self.poller = zmq.Poller()
        self.poller.register(self.frontend_communication, zmq.POLLIN)
        self.poller.register(self.backend_communication, zmq.POLLIN)

        # TODO:
        # need to bind the front and backend communication together
        # need to poll this connection?

        self.driver_processes = []
        # plugins are already collected
        self.plugin_manager = AudioPluginManager()
        # this should be a list of class instances
        # class_instance = self.plugin_manager.get_plugins()[0]

        # FIXME
        class_instance = PyAudioEnginePlugin

        invoked_plugin = class_instance(context,
                                        self.backend_adress,
                                        self.audio_subscription_address)

        thread_instance = Thread(target=invoked_plugin.run)
        self.driver_processes.append(thread_instance)

    def _handle_frontend_communication(self):
        frame = self.frontend_communication.recv_multipart()
        print('2nd socket frame', frame)
        # id
        id_ = frame.pop(0)
        # expect a blank frame here
        frame.pop(0)

        cmd_type = frame.pop(0)
        arg = frame.pop()       # optional arg
        cmd = frame.pop()       # cmd

        # NOTE: metadriver commands do NOT have a name attr
        name = None
        if not cmd_type == b'metadriver':
            pass
            # name = frame.pop()  # name, either driver name or instance id
        if cmd_type == b'instance' or cmd_type == b'driver':
            # FIXME: pretty sure the first part needs to be an socket id
            self.backend_communication.send_multipart((name,
                                                       cmd_type,
                                                       cmd,
                                                       arg))

        elif cmd_type == b'metadriver':
            if cmd == b'list_drivers':
                optional_arg = b''
                # NOTE: we want to `ping` the drivers to get address
                # so we'll send an empty command to get an empty back
                command = b''
                frame = (b'', command, optional_arg)
                self.backend_communication.send_multipart(frame)

    def _handle_backend_communication(self):
        frame = self.backend_communication.recv_multipart()
        # should get back all devices + a socket descriptor
        print('3rd socket frame', frame)

    def run(self):
        for thread in self.driver_processes:
            thread.start()

        while True:
            sockets = dict(self.poller.poll())

            if self.frontend_communication in sockets:
                self._handle_frontend_communication()
            elif self.backend_communication in sockets:
                self._handle_backend_communication()

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


def main(frontend_address='tcp://127.0.0.1:5561',
         backend_address='tcp://127.0.0.1:5562',
         audio_subscription_address='tcp://127.0.0.1:5655'):

    kwargs = {'frontend_address': frontend_address,
              'backend_address': backend_address,
              'audio_subscription_address': audio_subscription_address}

    communication_node = CommunicationNode(**kwargs)
    communication_node.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--frontend_address',
                        action='store',
                        default='tcp://127.0.0.1:5561')

    parser.add_argument('--backend_address',
                        action='store',
                        default='tcp://127.0.0.1:5562')

    parser.add_argument('--audio_subscription_address',
                        action='store',
                        default='tcp://127.0.0.1:5655')

    args = parser.parse_args()

    main(args.frontend_address,
         args.backend_address,
         args.audio_subscription_address)
