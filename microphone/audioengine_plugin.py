import abc

import zmq

# Drivers drive devices
class DriverCMD:
    invoke = 'invoke'
    update = 'update'
    restart = 'restart'
    details = 'details'
    list = 'list'

class DeviceCMD:
    record = 'record'

class AudioEnginePlugin(metaclass=abc.ABCMeta):
    def __init__(self, context=None, address=''):
        self._context = context or zmq.Context()
        address = address or 'inproc://microphone'
        self.socket = self._context.socket(zmq.ROUTER)
        self.socket.bind(address)
        # get socket id
        self.devices = {}

    def run(self):
        while True:
            frame = self.socket.recv_multipart()

    def get_devices(self):
        pass

    def get_default_device(self):
        pass

    def invoke_device(self, device):
        pass


class AudioEngineDevice(metaclass=abc.ABCMeta):
    pass
