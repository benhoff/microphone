import argparse
from subprocess import Popen
from threading import Thread

import zmq
import pluginmanager
from microphone.messaging import Messaging


class MetadriverCMD:
    list = 'list'
    active = 'active'


class Node(object):
    def __init__(self, context=None, **kwargs):
        self.driver_processes = []
        self.audio_subscription_address = kwargs.get('audio_subscription_address',
                                                     _AUDIO_SUBSCRIPTION_ADDRESS)

        self.messaging = Messaging(context, **kwargs)
        # plugins are already collected
        self.plugin_manager = pluginmanager.PluginInterface()
        self.plugin_manager.set_entry_points('microphone.audioengines')
        plugins, names = self.plugin_manager.collect_entry_point_plugins()

        # TODO: add in some logic here or something
        class_instance = plugins[0]
        invoked_plugin = class_instance(context,
                                        self.messaging.backend_address,
                                        self.audio_subscription_address)

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

def main(*args, **kwargs):
    """
    kwargs:
        frontend_address
        backend_address
        audio_subscription_address
    """

    communication_node = Node(*args, **kwargs)
    communication_node.run()


def _get_kwargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--frontend_address',
                        action='store',
                        default=_DEFAULT_FRONTEND)

    # TODO: Decide if this is needed
    # might could just bind to random port
    parser.add_argument('--backend_address',
                        action='store',
                        default=_DEFAULT_BACKEND)

    parser.add_argument('--audio_subscription_address',
                        action='store',
                        default=_AUDIO_SUBSCRIPTION_ADDRESS)

    return vars(parser.parse_args())


if __name__ == '__main__':
    kwargs = _get_kwargs()
    main(**kwargs)
