import io
import sys
import time
import wave
import logging
import argparse
import contextlib
from os import path

import pyaudio
import zmq

from vexmessage import create_vex_message, decode_vex_message

from microphone.command_manager import CommandManager

PYAUDIO_BIT_MAPPING = {8:  pyaudio.paInt8,
                       16: pyaudio.paInt16,
                       24: pyaudio.paInt24,
                       32: pyaudio.paInt32}


def bits_to_samplefmt(bits):
    if bits in PYAUDIO_BIT_MAPPING.keys():
        return PYAUDIO_BIT_MAPPING[bits]


class PyAudio:
    def __init__(self, messaging, settings):
        self._pyaudio = pyaudio.PyAudio()
        self.messaging = messaging
        self.command_manager = CommandManager(self, messaging)
        self._logger = logging.getLogger(__name__)
        self._logger.info("Initializing PyAudio. ALSA/Jack error messages " +
                          "that pop up during this process are normal and " +
                          "can usually be safely ignored.")
        # NOTE: pyaudio SPAMS the terminal, this seperates everything
        print('\n')
        self._logger.info("Initialization of PyAudio engine finished")

        self.devices = {}
        self.get_devices()

    def __del__(self):
        self._pyaudio.terminate()

    def run(self):
        messaging = self.messaging
        # TODO: create better type here
        startup_frame = create_vex_message('',
                                           'microphone',
                                           'STATUS',
                                           status='recording')

        messaging.publish_socket.send_multipart(startup_frame)

        while True:
            # NOTE: `frame` is a list of byte strings
            # Once we recv here, MUST reply in order to loop again!
            try:
                frame = self.messaging.subscribe_socket.recv_multipart()
            except KeyboardInterrupt:
                break

            msg = decode_vex_message(frame)

            if msg.type == 'CMD':
                self.command_manager.handle_command(msg)

    def get_devices(self, device_type='all'):
        num_devices = self._pyaudio.get_device_count()
        self._logger.debug('Found %d PyAudio devices', num_devices)
        for i in range(num_devices):
            info = self._pyaudio.get_device_info_by_index(i)
            name = info['name']
            if name in self.devices:
                continue
            else:
                self.devices[name] = PyAudioDevice(self, info)

        return self.devices
        """
        if device_type == plugin.audioengine.DEVICE_TYPE_ALL:
            return devs
        else:
            return [device for device in devs if device_type in device.types]
        """

    def invoke_device(self):
        pass

    def get_default_output_device(self):
        info = self._pyaudio.get_default_output_device_info()
        return PyAudioDevice(self, info)

    def get_default_device(self, type='input'):
        try:
            info = self._pyaudio.get_default_input_device_info()
        except IOError:
            devices = self.get_devices(device_type=type)
            if len(devices) == 0:
                msg = 'No %s devices available!' % direction
                self._logger.warning(msg)
                raise plugin.audioengine.DeviceNotFound(msg)
            try:
                device = self.devices['default']
            except KeyError:
                self._logger.warning('default device not found')
                # FIXME
                device = None
            return device
        else:
            return PyAudioDevice(self, info)


class PyAudioDevice:
    def __init__(self, engine, info, context=None, address='inproc://microphone'):
        super().__init__()
        self._logger = logging.getLogger(__name__)
        self._engine = engine
        self.info = info
        self._index = info['index']
        self._max_output_channels = info['maxOutputChannels']
        self._max_input_channels = info['maxInputChannels']
        # FIXME
        self._sample_width = self._engine._pyaudio.get_sample_size(pyaudio.paInt16)
        self._default_sample_rate = int(self.info['defaultSampleRate'])
        res_file = path.abspath(path.join(path.dirname(__file__),
                                           'resources'))

        wave_file = path.join(res_file, 'congo.wav')

        wf = wave.open(wave_file, 'rb')

        self._output_rate = wf.getframerate()
        self._output_format = wf.getsampwidth()
        self._output_channels = wf.getnchannels()
        self._output_file = wave_file
        wf.close()

        close_file = path.join(res_file, 'done.wav')
        wf = wave.open(close_file, 'rb')
        self._close_rate = wf.getframerate()
        self._close_format = wf.getsampwidth()
        self._close_channels = wf.getnchannels()
        self._close_file = close_file

    def supports_format(self, bits, channels, rate, output=False):
        req_dev_type = ('output' if output else 'input')
        sample_fmt = bits_to_samplefmt(bits)
        if not sample_fmt:
            return False
        direction = 'output' if output else 'input'
        fmt_info = {
            ('%s_device' % direction): self._index,
            ('%s_format' % direction): sample_fmt,
            ('%s_channels' % direction): channels,
            'rate': rate
        }
        try:
            supported = self._engine._pyaudio.is_format_supported(**fmt_info)
        except ValueError as e:
            if e.args in (('Sample format not supported', -9994),
                          ('Invalid sample rate', -9997),
                          ('Invalid number of channels', -9998)):
                return False
            else:
                raise
        else:
            return supported

    @contextlib.contextmanager
    def open_stream(self,
                    bits,
                    channels,
                    rate=None,
                    chunksize=1024,
                    output=True):

        if rate is None:
            rate = int(self.info['defaultSampleRate'])
        # Check if format is supported
        is_supported_fmt = self.supports_format(bits, channels, rate,
                                                output=output)
        if not is_supported_fmt:
            msg_fmt = ("PyAudioDevice {index} ({name}) doesn't support " +
                       "%s format (Int{bits}, {channels}-channel at" +
                       " {rate} Hz)") % ('output' if output else 'input')
            msg = msg_fmt.format(index=self.index,
                                 name=self.name,
                                 bits=bits,
                                 channels=channels,
                                 rate=rate)
            self._logger.critical(msg)
            raise plugin.audioengine.UnsupportedFormat(msg)
        # Everything looks fine, open the stream
        direction = ('output' if output else 'input')
        stream_kwargs = {
            'format': bits_to_samplefmt(bits),
            'channels': channels,
            'rate': rate,
            'output': output,
            'input': not output,
            ('%s_device_index' % direction): self._index,
            'frames_per_buffer': chunksize if output else chunksize*8  # Hacky
        }

        stream = self._engine._pyaudio.open(**stream_kwargs)
        """
        self._logger.debug("%s stream opened on device '%s' (%d Hz, %d " +
                           "channel, %d bit)", "output" if output else "input",
                           self.slug, rate, channels, bits)
        """
        try:
            yield stream
        finally:
            stream.close()
            """
            self._logger.debug("%s stream closed on device '%s'",
                               "output" if output else "input", self.slug)
            """

    def play_beep(self):
        chunksize = 1024
        f = self._engine._pyaudio.get_format_from_width(self._output_format)
        stream = self._engine._pyaudio.open(format=f,
                                    channels = self._output_channels,
                                    rate = self._output_rate,
                                    output=True)

        wf = wave.open(self._output_file)
        data = wf.readframes(chunksize)
        while len(data) > 0:
            stream.write(data)
            data = wf.readframes(chunksize)

        stream.stop_stream()
        stream.close()

    def play_done(self):
        chunksize = 1024
        f = self._engine._pyaudio.get_format_from_width(self._close_format)
        stream = self._engine._pyaudio.open(format=f,
                channels = self._close_channels,
                rate = self._output_rate,
                output=True)

        wf = wave.open(self._close_file)
        data = wf.readframes(chunksize)
        while len(data) > 0:
            stream.write(data)
            data = wf.readframes(chunksize)

        stream.stop_stream()
        stream.close()

    def record(self, chunksize, *args):
        channels = args[1]
        with self.open_stream(*args, chunksize=chunksize,
                              output=False) as stream:

            record_seconds = 5
            rate = int(self.info['defaultSampleRate'])
            steps = int(rate/chunksize * record_seconds)
            data_list = io.BytesIO()
            # NOTE: need the rate info and sample width for ASR
            for _ in range(steps):
                try:
                    data_list.write(stream.read(chunksize))
                except IOError as e:
                    if type(e.errno) is not int:
                        # Simple hack to work around the fact that thmt_from_width
                        # errno/strerror arguments were swapped in older
                        # PyAudio versions. This was fixed in upstream
                        # commit 1783aaf9bcc6f8bffc478cb5120ccb6f5091b3fb.
                        strerror, errno = e.errno, e.strerror
                    else:
                        strerror, errno = e.strerror, e.errno
                    self._logger.warning("IO error while reading from device" +
                                         " '%s': '%s' (Errno: %d)", self.slug,
                                         strerror, errno)

            return data_list.getvalue()
