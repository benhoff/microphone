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

    driver = kwargs.get('driver', 'pyaudio')
    reactor.start_driver(driver)

    # now, let's talk on our public face
    reactor.run()


if __name__ == '__main__':
    parser = MicArgParser()
    args = parser.parse_args()
    main()
