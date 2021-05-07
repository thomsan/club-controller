
from club_controller.misc.object_factory import ObjectFactory

from .client_type_id import ClientTypeId
from .gpio_client import GPIOClient
from .led_strip_client import LedStripClient
from .nec_led_strip_client import NECLedStripClient


def create_led_strip_client(uid, ip, port, mac, name, color, color_templates, effect_id, fps, frequency, num_pixels, sigma, **_ignored):
    return LedStripClient(uid, ip, port, mac, name, color, color_templates, effect_id, fps, frequency, num_pixels, sigma)

def create_nec_led_strip_client(uid, ip, port, mac, name, color, color_templates, effect_id, frequency, **_ignored):
    return NECLedStripClient(uid, ip, port, mac, name, color, color_templates, effect_id, frequency)

def create_gpio_client(uid, ip, port, mac, name, gpio_modes, **_ignored):
    return GPIOClient(uid, ip, port, mac, name, gpio_modes)


class ClientProvider(ObjectFactory):
    def get(self, client_type_id, **kwargs):
        # TODO find a better way
        # make sure kwargs contains all nec_led_strip fields
        for key, value in NECLedStripClient.get_default_properties().items():
            if not key in kwargs:
                kwargs[key] = value
        # make sure kwargs contains all led_strip fields
        for key, value in LedStripClient.get_default_properties().items():
            if not key in kwargs:
                kwargs[key] = value
        # make sure kwargs contains all gpio fields
        for key, value in GPIOClient.get_default_properties().items():
            if not key in kwargs:
                kwargs[key] = value
        print(kwargs)
        print(client_type_id)
        return self.create(client_type_id, **kwargs)


client_provider = ClientProvider()
client_provider.register_builder(ClientTypeId.LED_STRIP_CLIENT, create_led_strip_client)
client_provider.register_builder(ClientTypeId.GPIO_CLIENT, create_gpio_client)
client_provider.register_builder(ClientTypeId.NEC_LED_STRIP_CLIENT, create_nec_led_strip_client)
