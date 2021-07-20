
from club_controller.misc.object_factory import ObjectFactory

from .client_type_id import ClientTypeId
from .gpio_client import GPIOClient
from .led_strip_client import LedStripClient
from .nec_led_strip_client import NECLedStripClient


def create_led_strip_client(uid, ip, port, mac, name, mode, color, color_templates, effect_id, fps, frequency, num_pixels, filter, **_ignored):
    return LedStripClient(uid, ip, port, mac, name, mode, color, color_templates, effect_id, fps, frequency, num_pixels, filter)

def create_nec_led_strip_client(uid, ip, port, mac, name, color, color_templates, effect_id, frequency, **_ignored):
    return NECLedStripClient(uid, ip, port, mac, name, color, color_templates, effect_id, frequency)

def create_gpio_client(uid, ip, port, mac, name, gpio_modes, **_ignored):
    return GPIOClient(uid, ip, port, mac, name, gpio_modes)


class ClientProvider(ObjectFactory):
    def get(self, client_type_id, **kwargs):
        if client_type_id == ClientTypeId.LED_STRIP_CLIENT:
            default_kwargs = LedStripClient.get_default_properties().items();
        elif client_type_id == ClientTypeId.NEC_LED_STRIP_CLIENT:
            default_kwargs = NECLedStripClient.get_default_properties().items()
        elif client_type_id == ClientTypeId.GPIO_CLIENT:
            default_kwargs = GPIOClient.get_default_properties().items()
        else:
            default_kwargs = []

        for key, value in default_kwargs:
            if not key in kwargs:
                kwargs[key] = value

        return self.create(client_type_id, **kwargs)


client_provider = ClientProvider()
client_provider.register_builder(ClientTypeId.LED_STRIP_CLIENT, create_led_strip_client)
client_provider.register_builder(ClientTypeId.GPIO_CLIENT, create_gpio_client)
client_provider.register_builder(ClientTypeId.NEC_LED_STRIP_CLIENT, create_nec_led_strip_client)
