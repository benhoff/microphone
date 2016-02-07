import pluginmanager


class AudioPluginManager(pluginmanager.PluginInterface):
    def __init__(self):
        super().__init__()
        self.set_entry_points('microphone.audioengines')
        self.plugin_manager.instantiate_classes = False
        self.collect_entry_point_plugins()
