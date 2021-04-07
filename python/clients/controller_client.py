from .client import Client, ClientConfig, ClientTypeId


class ConrollerConfig(ClientConfig):
    def __init__(self, ip, port, name, web_socket_url):
        self.web_socket_url = web_socket_url
        super().__init__(self, ip, port, name)

    @staticmethod
    def object_decoder(self, obj):
        if '__type__' in obj and obj['__type__'] == 'ConrollerConfig':
            return ConrollerConfig(obj['ip'], obj['port'], obj['name'], obj['web_socket_url'])
        return obj


class ControllerClient(Client):
    def __init__(self, config):
        # TODO check config
        super().__init__(ClientTypeId.LED_STRIP_CLIENT, config)

    def on_connected(self):
        if __debug__:
            print("ControllerClient connected")
