from .client import Client, ClientTypeId


class ControllerClient(Client):
    def __init__(self, config, web_socket_url):
        # TODO check config
        self.web_socket_url = web_socket_url
        super().__init__(int(ClientTypeId.LED_STRIP_CLIENT), config)

    def on_connected(self):
        if __debug__:
            print("ControllerClient connected")
