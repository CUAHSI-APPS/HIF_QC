#The Configuration Interface Will Provide Tools
# to make the configuartion of our data sources simpler
# from the point of view of an end user

class ConfigurationInterface:

    __metaclass__ = ABCMeta

    def __init__(self, ConfigSource = None):
        self.ConfigSource = ConfigSource

    @abstractmethod
    def ValidateConnection(self):
        return


class DataBaseConfigurationInterface(ConfigurationInterface):

    def __init__(self, ConfigSource = None):
        self.ConfigSource = ConfigSource

    def ValidateConnection(self):
