import zmq


class Messaging:
    def __init__(self, context=None, **kwargs):
        self._context = context or zmq.Context()
        self.frontend_address = kwargs.get('frontend_address',
                                           'tcp://127.0.0.1:5561')

        # this might need to be defaulted to a tcp device?
        self.backend_address = kwargs.get('backend_address',
                                         'tcp://127.0.0.1:5562')

        # create the public facing communication socket
        self.frontend_communication = self._context.socket(zmq.ROUTER)
        self.frontend_communication.bind(self.frontend_address)

        # create internal communications
        self.backend_communication = self._context.socket(zmq.ROUTER)
        self.backend_communication.bind(self.backend_address)

        self.poller = zmq.Poller()
        self.poller.register(self.frontend_communication, zmq.POLLIN)
        self.poller.register(self.backend_communication, zmq.POLLIN)
        self._microphone_sockets = []

    def run(self):
        while True:
            try:
                sockets = dict(self.poller.poll())
            except KeyboardInterrupt:
                break

            if self.frontend_communication in sockets:
                self._handle_frontend_communication()
            elif self.backend_communication in sockets:
                self._handle_backend_communication()

    def _handle_frontend_communication(self):
        frame = self.frontend_communication.recv_multipart()
        # id
        id_ = frame.pop(0)
        # expect a blank frame here
        frame.pop(0)

        cmd_type = frame.pop(0)
        cmd = frame.pop(0)       # cmd
        arg = frame.pop(0)       # optional arg

        # NOTE: metadriver commands do NOT have a name attr
        name = None
        if not cmd_type == b'metadriver':
            pass
            # optional_arg = frame.pop()  # name, either driver name or instance id

        if cmd_type == b'instance' or cmd_type == b'driver':
            if cmd == b'record':
                driver_socket_id = arg
                optional_arg = b'default'
                # FIXME: Should be able to pass in the original id
                frame = (driver_socket_id, b'', cmd, optional_arg)
                self.backend_communication.send_multipart(frame)

        elif cmd_type == b'metadriver':
            if cmd == b'list_drivers':
                # NOTE: Might not work
                frame = (id_, b'', *self._microphone_sockets)
                self.frontend_communication.send_multipart(frame)

    def _handle_backend_communication(self):
        frame = self.backend_communication.recv_multipart()
        if frame[2] == b'READY':
            id_ = frame[0]
            self._microphone_sockets.append(id_)
