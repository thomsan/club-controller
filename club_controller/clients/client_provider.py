
from club_controller.misc.object_factory import ObjectFactory

from .client_type_id import ClientTypeId
from .gpio_client import GPIOClient
from .led_strip_client import LedStripClient


def create_led_strip_client(uid, ip, port, mac, name, color, color_templates, effect_id, fps, frequency, num_pixels, sigma, **_ignored):
    return LedStripClient(uid, ip, port, mac, name, color, color_templates, effect_id, fps, frequency, num_pixels, sigma)


def create_gpio_client(uid, ip, port, mac, name, gpio_modes, **_ignored):
    return GPIOClient(uid, ip, port, mac, name, gpio_modes)


class ClientProvider(ObjectFactory):
    def get(self, client_type_id, **kwargs):
        # make sure kwargs contains all led_strip fields
        for key, value in LedStripClient.get_default_properties().items():
            if not key in kwargs:
                kwargs[key] = value
        # make sure kwargs contains all gpio fields
        for key, value in GPIOClient.get_default_properties().items():
            if not key in kwargs:
                kwargs[key] = value
        return self.create(client_type_id, **kwargs)


client_provider = ClientProvider()
client_provider.register_builder(ClientTypeId.LED_STRIP_CLIENT, create_led_strip_client)
client_provider.register_builder(ClientTypeId.GPIO_CLIENT, create_gpio_client)
