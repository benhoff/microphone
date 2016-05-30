class CommandManager:
    def __init__(self, pyaudio, messaging):
        self.pyaudio = pyaudio
        self.messaging = messaging

    def handle_command(self, msg):
        command = msg.contents[0]

        if command == 'list devices':
            devices = self.pyaudio.get_devices()
            frame = create_vex_message(msg.source,
                                       'microphone',
                                       'MSG',
                                       devices)

            messaging.communication_socket.send_multipart(frame)
        elif command == 'record':
            device = self.pyaudio.get_default_device()

            # FIXME
            bits = 16
            channels  = 2
            chunksize = 1024
            device.record(chunksize, bits, channels)
            messaging.communication_socket.send(b'')
        elif command == b'':
            messaging.communication_socket.send(b'')
        else:
            w = 'Did not parse packet in pyaudio correctly, sending blank'
            self.pyaudio._logger.warn(w)
            messaging.communication_socket.send(b'')
