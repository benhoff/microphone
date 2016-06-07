from vexmessage import create_vex_message


class CommandManager:
    def __init__(self, audio_driver, messaging):
        self.audio_driver = audio_driver
        self.messaging = messaging

    def handle_command(self, msg):
        command = msg.contents[0]

        if command == 'list devices':
            devices = self.audio_driver.get_devices()
            frame = create_vex_message(msg.source,
                                       'microphone',
                                       'MSG',
                                       devices)

            messaging.communication_socket.send_multipart(frame)
        elif command == 'record':
            device = self.audio_driver.get_default_device()

            # FIXME: pass in in settings instead
            bits = 16
            channels  = 2
            chunksize = 1024
            device.record(chunksize, bits, channels)
