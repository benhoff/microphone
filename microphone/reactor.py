import re
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
    CMD_DRIVER = 'microphone.driver.{driver_name}.{cmd}.{arg}'
    CMD_INSTANCE = 'microphone.instance.{id}.{cmd}.{arg}'
    CMD_METADRIVER = 'microphone.metadriver.{cmd}.{arg}'

    def __init__(self, context=None, **kwargs):
        context = context or zmq.Context()
        self.address_frontend = kwargs.get('address_frontend',
                                           'tcp://*:5556')

        self.address_backend = kwargs.get('address_backend',
                                          'inproc://microphone')

        # create the public facing communication socket
        self.frontend_communication = context.socket(zmq.ROUTER)
        self.frontend_communication.bind(self.address_frontend)

        # create internal communications
        self.backend_communication = context.socket(zmq.DEALER)
        self.backend_communication.bind(self.address_backend)
        self.plugin_manager = AudioPluginManager()

    def handle_instance_command(self, command, id_):
        get = self.plugin_manager.get_instances

    def handle_driver_command(self, command, driver):
        pass

    def handle_metadriver_command(self, command):
        pass

    def run(self):
        frontend = self.frontend_communication
        while True:
            frame = frontend.recv_multipart()
            frame.pop(0)            # id
            cmd_type = frame.pop(0) # cmd_typ
            arg = frame.pop()       # optional arg
            cmd = frame.pop()       # cmd
            name = None
            if not cmd_type == 'metadriver':
                name = frame.pop()  # name, either driver name or instance id
            if cmd_type == 'instance':
                self.backend_communication.send_multipart([name,
                                                           cmd,
                                                           arg])




    def start_driver(self, driver):
        driver = self.plugin_manager.get_plugins(_get_driver(driver))
        # TODO: finish

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
