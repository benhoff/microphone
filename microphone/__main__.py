import sys
import time
import argparse
from os import path
from multiprocessing import Process

import zmq

from reactor import Reactor
from garbage import G
from _argparser import MicArgParser




def record(self):
    context = zmq.Context()

    publish_socket = context.socket(zmq.PUB)
    publish_socket.connect(address)

    reciever = context.socket(zmq.PAIR)
    reciever.bind('inproc://microphone')

    while True:
        msg = reciever.recv()
        if msg:
            frames = []
            for _ in range(0, msg):
                frames.append(audio.record())

            publish_socket.send_multipart(frames)

def set_up_device(driver, **kwargs):
    rate = kwargs.get('rate', _RATE)
    bits = kwargs.get('bits', _BITS)
    channels = kwargs.get('channel', _CHANNEL)
    chunksize = kwargs.get('chunksize', _CHUNKSIZE)


def _get_driver(plugins):
    for plugin in plugins:
        if plugin.__name__ == driver:
            return plugin

def set_up_driver(plugin_interface, driver):
    driver = plugin_interface.get_plugins(_get_driver)
    return driver()


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
    context = zmq.Context()
    garbage = G(context)
    reactor = Reactor(context)

    # get the name of the driver specified and instantiate
    driver = kwargs.get('driver', _DRIVER)
    driver = set_up_driver(plugin_interface, driver)
    # now default to setting up a device
    set_up_device(driver, kwargs)

    # now, let's talk on our public face
    while True:
        msg = frontend_communication.recv()


if __name__ == '__main__':
    # publish_address = sys.argv[1] if len(sys.argv) > 1 else 'tcp:///*:5555'
    # response_address = 
    parser = MicArgParser()
    args = parser.parse_args()
    # TODO: debug
    print(args)
    main()
