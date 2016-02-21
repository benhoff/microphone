import sys
import wave
import subprocess
import pyaudio
import time
from os import path
import zmq


address = 'tcp://127.0.0.1:5555'
context = zmq.Context()
dealer_socket = context.socket(zmq.DEALER)
dealer_socket.bind(address)

audio_socket_address = 'tcp://127.0.0.1:5556'
audio_socket = context.socket(zmq.SUB)
audio_socket.bind(audio_socket_address)
audio_socket.setsockopt_string(zmq.SUBSCRIBE, '')

audio_filepath = path.join(path.dirname(__file__),
                           'audioengines',
                           'pyaudio_ae',
                           '__main__.py')

subprocess.Popen((sys.executable, audio_filepath, address, audio_socket_address))
time.sleep(2)

while True:
    # response socket expects to see an empty first frame
    empty = b''

    command = b'list_devices'
    optional_arg = b''
    frame = (empty, command, optional_arg)

    dealer_socket.send_multipart(frame)
    reply = dealer_socket.recv_multipart()

    command = b'record'
    optional_arg = b'default'
    frame = (empty, command, optional_arg)
    """
    f = wave.open('audio.wav', mode='wb')
    f.setnchannels(2)
    p = pyaudio.PyAudio()
    f.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    f.setframerate(p.get_default_input_device_info()['defaultSampleRate'])
    """
    dealer_socket.send_multipart(frame)
    # record_reply = dealer_socket.recv_multipart()
    for _ in range(215):
        frame = audio_socket.recv()
        # f.writeframes(frame)

    # f.close()
    break
