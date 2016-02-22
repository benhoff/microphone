import sys
import subprocess
from os import path
import zmq
from _argparser import MicArgParser


def main(multiprocess=True, *args, **kwargs):
    """
    kwargs:
        'publish_address': in the form of `tcp:///*:5555`
        or any other zeromq address format. IE `ipc:///*:5555`

        'response_address': in the form of `tcp:///*:5555`
        or any other zeromq address format. IE `ipc:///*:5555`
    """
    directory = path.dirname(__file__)
    # the communication node is responsible for launching the audio devices
    communication_node_filepath = path.join(directory,
                                            'communication_node.py')

    audio_node_filepath = path.join(directory,
                                    'audio_node.py')

    python_interp = sys.executable
    audio_node_args = ()
    audio_node_process = subprocess.Popen((python_interp,
                                           audio_node_filepath,
                                           *audio_node_args))

    communication_node_args = ()
    commmunication_node_process = subprocess.Popen((python_interp,
                                                    communication_node_filepath,
                                                    *communication_node_args))

    context = zmq.Context()
    socket = zmq.socket(zmq.REP)
    socket.bind('tcp://localhost:5560')
    while True:
        frame = socket.recv()
        print('msg recieved', frame)
        if frame == b'restart communication node':
            pass
        elif frame == b'restart audio node':
            pass


if __name__ == '__main__':
    parser = MicArgParser()
    args = parser.parse_args()
    main(*args)
