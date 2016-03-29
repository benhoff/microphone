import argparse
from subprocess import Popen
from threading import Thread

import zmq
from microphone.plugin_manager import AudioPluginManager
from microphone.communication_messaging import CommunicationMessaging


class MetadriverCMD:
    list = 'list'
    active = 'active'


class CommunicationNode(object):
    def __init__(self, context=None, **kwargs):
        self.driver_processes = []
        self.messaging = CommunicationMessaging(context, **kwargs)
        # plugins are already collected
        self.plugin_manager = AudioPluginManager()

        plugins = self.plugin_manager.get_plugins()
        # TODO: add in some logic here or something
        class_instance = plugins[0]
        invoked_plugin = class_instance(context,
                                        self.messaging.backend_address,
                                        self.messaging.audio_subscription_address)

        thread_instance = Thread(target=invoked_plugin.run)
        self.driver_processes.append(thread_instance)


    def run(self):
        for thread in self.driver_processes:
            thread.start()

        self.messaging.run()

    def invoke_driver(self, driver):
        """
        driver's manage multiple devices
        """
        driver = self.plugin_manager.get_plugins(_get_driver(driver))
        # TODO: Implement

def _get_driver(name):
    def filter_function(plugins):
        for plugin in plugins:
            if plugin.__name__ == name:
                return plugin

    return filter_function


_DEFAULT_FRONTEND = 'tcp://127.0.0.1:5561'
_DEFAULT_BACKEND = 'tcp://127.0.0.1:5562'
_AUDIO_SUBSCRIPTION_ADDRESS = 'tcp://127.0.0.1:5655'

def main(frontend_address=_DEFAULT_FRONTEND,
         backend_address=_DEFAULT_BACKEND,
         audio_subscription_address=_AUDIO_SUBSCRIPTION_ADDRESS):

    kwargs = {'frontend_address': frontend_address,
              'backend_address': backend_address,
              'audio_subscription_address': audio_subscription_address}

    communication_node = CommunicationNode(**kwargs)
    communication_node.run()


def _get_kwargs():
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

    return vars(parser.parse_args())


if __name__ == '__main__':
    kwargs = _get_kwargs()
    main(**kwargs)
