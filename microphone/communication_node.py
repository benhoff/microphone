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
        self.backend_communication = self._context.socket(zmq.ROUTER)
        self.backend_communication.bind(self.backend_adress)

        self.poller = zmq.Poller()
        self.poller.register(self.frontend_communication, zmq.POLLIN)
        self.poller.register(self.backend_communication, zmq.POLLIN)

        self.driver_processes = []
        # plugins are already collected
        self.plugin_manager = AudioPluginManager()
        """
        # this should be a list of class instances
        plugins = self.plugin_manager.get_plugins()
        class_instance = plugins[0]
        print(plugins, class_instance)
        """

        # FIXME
        class_instance = PyAudioEnginePlugin

        invoked_plugin = class_instance(context,
                                        self.backend_adress,
                                        self.audio_subscription_address)

        thread_instance = Thread(target=invoked_plugin.run)
        self.driver_processes.append(thread_instance)

        self._microphone_sockets = []

    def _handle_frontend_communication(self):
        frame = self.frontend_communication.recv_multipart()
        # id
        id_ = frame.pop(0)
        # expect a blank frame here
        frame.pop(0)

        cmd_type = frame.pop(0)
        cmd = frame.pop(0)       # cmd
        arg = frame.pop(0)       # optional arg

        # NOTE: metadriver commands do NOT have a name attr
        name = None
        if not cmd_type == b'metadriver':
            pass
            # optional_arg = frame.pop()  # name, either driver name or instance id

        if cmd_type == b'instance' or cmd_type == b'driver':
            if cmd == b'record':
                driver_socket_id = arg
                optional_arg = b'default'
                # FIXME: Should be able to pass in the original id
                frame = (driver_socket_id, b'', cmd, optional_arg)
                self.backend_communication.send_multipart(frame)

        elif cmd_type == b'metadriver':
            if cmd == b'list_drivers':
                # NOTE: Might not work
                frame = (id_, b'', *self._microphone_sockets)
                self.frontend_communication.send_multipart(frame)

    def _handle_backend_communication(self):
        frame = self.backend_communication.recv_multipart()
        if frame[2] == b'READY':
            id_ = frame[0]
            self._microphone_sockets.append(id_)

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
