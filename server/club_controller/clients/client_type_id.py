from enum import IntEnum

class ClientTypeId(IntEnum):
    LED_STRIP_CLIENT = 0
    CONTROLLER_CLIENT = 1
    GPIO_CLIENT = 2
    SMOKE_MACHINE_CLIENT = 3
    NEC_LED_STRIP_CLIENT = 4
