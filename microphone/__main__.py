import pluginmanager
from vexbot.argenvconfig import ArgEnvConfig

from microphone.messaging import Messaging


def main(context=None, *args, **kwargs):
    """
    kwargs:
        'publish_address': in the form of `tcp:///*:5555`
        or any other zeromq address format. IE `ipc:///*:5555`

        'response_address': in the form of `tcp:///*:5555`
        or any other zeromq address format. IE `ipc:///*:5555`
    """
    # Get configuration, settings filepath and load the settings up
    config = _get_config()
    settings_filepath = config.get('settings_path')
    settings = config.load_settings(settings_filepath)

    plugin_manager = pluginmanager.PluginInterface()
    plugin_manager.set_entry_points('microphone.audioengines')
    plugins, names = plugin_manager.collect_entry_point_plugins()

    audio_driver = settings.get('audio_driver', 'pyaudio')

    # FIXME: No idea what error the index command would throw
    # if the index isn't found
    audio_driver_index = names.index(audio_driver)
    # NOTE: `AudioDriver` is a class
    AudioDriver = plugins[audio_driver_index]

    # NOTE: Assume that a computer will only use one audio driver?

    # Also assume that microphones may be physcially displaced from each other
    # which means that they might record simultaneously
    messaging = Messaging(settings)
    audio_driver = AudioDriver(messaging, settings)

    audio_driver.run()


def _get_config():
    config = ArgEnvConfig()
    config.add_argument('--settings_path',
                        default='settings.yml',
                        action='store')

    return config


if __name__ == '__main__':
    main()
