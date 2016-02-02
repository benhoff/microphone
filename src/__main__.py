import sys
import argparse
from os import path

import zmq
import pluginmanager

from .audioengine_plugin import AudioEnginePlugin


def main(*args, **kwargs):
    """
    kwargs:
        'publish_address': in the form of `tcp:///*:5555`
        or any other zeromq address format. IE `ipc:///*:5555`

        'response_address': in the form of `tcp:///*:5555`
        or any other zeromq address format. IE `ipc:///*:5555`
    """
    publish_address = kwargs.get('publish_address',
                                 'tcp:///*:5555')

    response_address = kwargs.get('response_address',
                                  'tcp:///*:5556')

    context = zmq.Context()
    publish_socket = context.socket(zmq.PUB)
    publish_socket.connect(address)
    response_socket = context.socket(REP)
    response_socket.bind(response_address)

    plugin_interface = pluginmanager.PluginInterface()
    plugin_dir = path.join(path.dirname(__file__),
                           'audioengines'))

    plugin_interface.set_plugin_directories(plugin_dir)
    plugin_interface.track_site_package_paths()


    while True:
        msg = response_socket.recv()

if __name__ == '__main__':
    # publish_address = sys.argv[1] if len(sys.argv) > 1 else 'tcp:///*:5555'
    # response_address = 
    parser = argparse.ArgumentParser(prog='Vex',
                                     description='audio capture')

    parser.add_argument(['--provider', '-p'],
                        action='store')

    parser.add_argument(['--publish_address'], action='store')
    parser.add_argument(['--response_address', '-r'], action='store')
    args = parser.parse_args()
    # TODO: debug
    print(args)
    main()
