import sys
import wave
import subprocess
import pyaudio
import time
from os import path
import zmq
import atexit


context = zmq.Context()
request_socket = context.socket(zmq.REQ)
request_socket.connect('tcp://127.0.0.1:5561')

directory = path.dirname(__file__)

communication_node = path.join(directory,
                               'communication_node.py')

args = (sys.executable,
        communication_node)

subprocess = subprocess.Popen(args)

def _kill_subprocess():
    subprocess.kill()

atexit.register(_kill_subprocess)

while True:
    command_type = b'metadriver'
    command = b'list_drivers'
    optional_arg = b''
    frame = (command_type, command, optional_arg)

    request_socket.send_multipart(frame)
    reply = request_socket.recv_multipart()

    # reply has all the avaiable microphone recording software IDs
    record_id = reply[0]

    # response socket expects to see an empty first frame
    command_type = b'driver'
    command = b'record'
    optional_arg = record_id

    frame = (command_type, command, optional_arg)

    request_socket.send_multipart(frame)
    reply = request_socket.recv_multipart()
    print(reply)

    """
    command = b'record'
    optional_arg = b'default'
    frame = (empty, command, optional_arg)
    f = wave.open('audio.wav', mode='wb')
    f.setnchannels(2)
    p = pyaudio.PyAudio()
    f.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    f.setframerate(p.get_default_input_device_info()['defaultSampleRate'])

    dealer_socket.send_multipart(frame)
    # record_reply = dealer_socket.recv_multipart()
    for _ in range(215):
        frame = audio_socket.recv()
        f.writeframes(frame)

    f.close()
    """
