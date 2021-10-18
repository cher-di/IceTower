import logging

import gpiozero
import psutil

from typing import Callable, Sequence


AVAILABLE_GPIO_PINS = list(range(2, 28))


class IceTower(gpiozero.OutputDevice):

    def __init__(self, pin: int):
        super(IceTower, self).__init__(pin, initial_value=None)

    def on(self):
        logging.info('ON ice tower')
        super(IceTower, self).on()

    def off(self):
        logging.info('OFF ice tower')
        super(IceTower, self).off()

    def toggle(self):
        logging.info('TOGGLE ice tower')
        return super(IceTower, self).toggle()


def current_cpu_temperature():
    return psutil.sensors_temperatures()['cpu_thermal'][0].current


def count_percentage(values: Sequence, comparator: Callable):
    suitable = list(filter(comparator, values))
    return len(suitable) / len(values) * 100
