import pprint


class CommandManager:
    def __init__(self, audio_driver, messaging):
        self.audio_driver = audio_driver
        self.messaging = messaging

        self._devices = {}
        self._devices['output'] = self.audio_driver.get_default_output_device()
        self._devices['input'] = self.audio_driver.get_default_device()

    def handle_command(self, msg):
        command = msg.contents.get('command')

        if command == 'list devices':
            devices = self.audio_driver.get_devices()
            self.messaging.send_response(msg.source,
                                         response=pprint.pformat(devices),
                                         original=command)

        elif command == 'record':
            bits = msg.contents.get('bits', 16)
            channels = msg.contents.get('channels', 1)
            chunksize = msg.contents.get('chunksize', 1024)

            beeper = self._devices['output']
            device = self._devices['input']

            beeper.play_beep()
            audio = device.record(chunksize, bits, channels)
            beeper.play_done()

            self.messaging.send_audio(msg.source,
                                      audio=audio,
                                      number_channels=channels,
                                      sample_width=device._sample_width,
                                      sample_rate=device._default_sample_rate)
