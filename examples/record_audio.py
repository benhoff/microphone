import sys
import wave
import subprocess
import pyaudio
import time
import atexit
import contextlib

from os import path
import zmq


@contextlib.contextmanager
def _create_file():
    """
    Returns a file handle which is used to record audio
    """
    f = wave.open('audio.wav', mode='wb')
    f.setnchannels(2)
    p = pyaudio.PyAudio()
    f.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    f.setframerate(p.get_default_input_device_info()['defaultSampleRate'])
    try:
        yield f
    finally:
        f.close()


def main():
    # using messaging library. Create the sockets for messaging
    context = zmq.Context()
    request_socket = context.socket(zmq.REQ)
    frontend_address = 'tcp://127.0.0.1:6910'
    request_socket.connect(frontend_address)
    audio_socket_address = 'tcp://127.0.0.1:6823'
    audio_socket = context.socket(zmq.SUB)
    audio_socket.setsockopt(zmq.SUBSCRIBE, b'')

    file_dir = path.dirname(__file__)
    src_dir = path.join('..', 'microphone')

    communication_node = path.join(src_dir,
                                   'communication_node.py')

    args = (sys.executable,
            communication_node,
            '--frontend_address',
            frontend_address,
            '--audio_subscription_address',
            audio_socket_address)

    subprocess_ = subprocess.Popen(args)

    def _kill_subprocess():
        subprocess_.kill()

    atexit.register(_kill_subprocess)
    # First thing we want is a driver socket ID
    command_type = b'metadriver'
    command = b'list_drivers'
    optional_arg = b''
    frame = (command_type, command, optional_arg)

    request_socket.send_multipart(frame)
    reply = request_socket.recv_multipart()

    # reply has all the avaiable microphone recording software IDs
    # grab the first one
    record_id = reply[0]

    # create our file as well
    # f = _create_file()

    command_type = b'driver'
    command = b'record'
    optional_arg = record_id


    frame = (command_type, command, optional_arg)

    # record request!
    request_socket.send_multipart(frame)

    """
    frames = audio_socket.recv_multipart()
    # this is the rate
    frames.pop(0)
    # this is the sample width
    frames.pop(0)
    for frame in frames:
        f.writeframes(frame)

    f.close()
    """

if __name__ == '__main__':
    main()
