from threading import Thread
import zmq
from plugin_manager import AudioPluginManager


class MetadriverCMD:
    list = 'list'
    active = 'active'


class DriverCMD:
    invoke = 'invoke'
    update = 'update'
    restart = 'restart'
    details = 'details'
    list = 'list'


class InstanceCMD:
    record = 'record'
    delete = 'delete'


class Reactor(object):
    def __init__(self, context=None, **kwargs):
        self._context = context or zmq.Context()
        self.address_frontend = kwargs.get('address_frontend',
                                           'tcp://*:5556')

        self.address_backend = kwargs.get('address_backend',
                                          'inproc://microphone')

        # create the public facing communication socket
        self.frontend_communication = self._context.socket(zmq.ROUTER)
        self.frontend_communication.bind(self.address_frontend)

        # create internal communications
        self.backend_communication = self._context.socket(zmq.DEALER)
        self.backend_communication.bind(self.address_backend)
        self.plugin_manager = AudioPluginManager()


    def run(self):
        frontend = self.frontend_communication
        while True:
            frame = frontend.recv_multipart()
            frame.pop(0)            # id
            cmd_type = frame.pop(0)
            arg = frame.pop()       # optional arg
            cmd = frame.pop()       # cmd
            # NOTE: metadriver commands do NOT have a name attr
            name = None
            if not cmd_type == b'metadriver':
                name = frame.pop()  # name, either driver name or instance id
            if cmd_type == b'instance':
                self.backend_communication.send_multipart([name,
                                                           cmd,
                                                           arg])

            elif cmd_type == b'driver':
                # update
                # restart
                # details ?
                if cmd == b'invoke':
                    self.invoke_device(name.decode('utf-8'),
                                       arg.decode('utf-8'))

                elif cmd == b'list':
                    self.send_driver_details(name.decode('utf-8'),
                                             args.decode('utf-8'))

            elif cmd_type == b'metadriver':
                pass

    def send_driver_details(self, driver, default=None):
        driver = self.plugin_manager.get_plugins(_get_driver(driver))
        if default:
            details = driver.get_default_device()
        else:
            details = driver.get_devices()
        details = [x.encode("ascii") for x in details]
        self.frontend_communication.send_multipart(*details)

    def track_device(self, driver, device):
        driver = self.plugin_manager.get_plugins(_get_driver(driver))
        device = driver.get_device(device)

    def invoke_device(self, driver, instance):
        """
        device's are single microphones
        """
        driver = self.plugin_manager.get_plugins(_get_driver(driver))
        device = driver.get_device(instance)

    def invoke_driver(self, driver):
        """
        driver's manage multiple devices
        """
        driver = self.plugin_manager.get_plugins(_get_driver(driver))
        self.plugin_manager.add_plugins(driver())
        self.frontend_communication.send_multipart([b"driver", b"invoked"])

def _get_instance(id_):
    def filter_function(instances):
        for instance in instances:
            if id(instance) == id_:
                return instance
    return filter_function

def _get_driver(name):
    def filter_function(plugins):
        for plugin in plugins:
            if plugin.__name__ == name:
                return plugin

    return filter_function
