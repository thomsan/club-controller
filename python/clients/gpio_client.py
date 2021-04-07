from .client import Client, ClientConfig, ClientTypeId


class GPIOConfig(ClientConfig):
    def __init__(self, ip, port, name, n_gpio_pins):
        self.n_gpio_pins = n_gpio_pins
        self.values = bytearray(n_gpio_pins)
        super().__init__(self, ip, port, name)


    @staticmethod
    def object_decoder(self, obj):
        if '__type__' in obj and obj['__type__'] == 'GPIOConfig':

            return GPIOConfig(obj['ip'], obj['port'], obj['name'], obj['n_gpio_pins'])
        return obj


class GPIOClient(Client):
    def __init__(self, config):
        self.config = config
        super().__init__(ClientTypeId.GPIO_CLIENT, self.config)
