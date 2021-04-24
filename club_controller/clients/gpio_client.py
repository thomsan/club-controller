from .client import Client
from .client_type_id import ClientTypeId


class GPIOClient(Client):
    def __init__(self, config):
        self.config = config
        super().__init__(int(ClientTypeId.GPIO_CLIENT), self.config)
