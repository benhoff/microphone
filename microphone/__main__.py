import sys
import argparse
import asyncio
from os import path

import zmq
import zmq.asyncio
import pluginmanager

async def record(audio, port):
    audio.record()


_RATE = 160000
_BITS = 16
_CHANNEL = 1
_CHUNKSIZE = 1024
_DRIVER = 'pyaudio'
_PUBLISH_ADDRESS = 'tcp:///*:5555'
_RESPONSE_ADDRESS = 'tcp:///*:5556'

def main(*args, **kwargs):
    """
    kwargs:
        'publish_address': in the form of `tcp:///*:5555`
        or any other zeromq address format. IE `ipc:///*:5555`

        'response_address': in the form of `tcp:///*:5555`
        or any other zeromq address format. IE `ipc:///*:5555`

        'rate'

        'bits'

        'channel'

        'chunksize'
    """

    publish_address = kwargs.get('publish_address',
                                 _PUBLISH_ADDRESS)

    response_address = kwargs.get('response_address',
                                  _RESPONSE_ADDRESS)

    rate = kwargs.get('rate', _RATE)
    bits = kwargs.get('bits', _BITS)
    channels = kwargs.get('channel', _CHANNEL)
    chunksize = kwargs.get('chunksize', _CHUNKSIZE)
    driver = kwargs.get('driver', _DRIVER)

    context = zmq.asyncio.Context()
    loop = zmq.asyncio.ZMQEventLoop()
    asyncio.set_event_loop(loop)

    publish_socket = context.socket(zmq.PUB)
    publish_socket.connect(address)

    response_socket = context.socket(REP)
    response_socket.bind(response_address)

    plugin_interface = pluginmanager.PluginInterface()
    plugin_interface.set_entry_points('microphone.audioengines')

    plugin_interface.plugin_manager.instantiate_classes = False
    plugin_interface.collect_entry_point_plugins()
    def get_driver(plugins):
        for plugin in plugins:
            if plugin.__name__ == driver:
                return plugin
    plugin = plugin_interface.get_plugins(get_driver)
    audio = plugin()

    while True:
        msg = yield from response_socket.recv_string()
        if msg:
            yield from record(audio)


if __name__ == '__main__':
    # publish_address = sys.argv[1] if len(sys.argv) > 1 else 'tcp:///*:5555'
    # response_address = 
    parser = argparse.ArgumentParser(prog='Vex',
                                     description='audio capture')

    parser.add_argument(('--driver', '-d'),
                        action='store',
                        default=_DRIVER)

    parser.add_argument(('--publish_address'),
                        action='store',
                        default=_PUBLISH_ADDRESS)

    parser.add_argument(('--response_address'),
                         action='store',
                         default=_RESPONSE_ADDRESS)

    parser.add_argument('rate', action='store', default=_RATE, type=int)
    parser.add_argument('bits', action='store', default=_BITS, type=int)
    parser.add_argument('chunksize', action='store', default=_CHUNKSIZE, type=int)
    parser.add_argument('channel', action='store', default=_CHANNEL, type=int)
    args = parser.parse_args()
    # TODO: debug
    print(args)
    main()
