import argparse
import logging
import signal
import sys
import time

import gpiozero
import psutil

from collections import deque
from typing import Sequence, Callable

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s')


AVAILABLE_GPIO_PINS = list(range(2, 28))

TOWER = None


def exit_gracefully(signum, frame):
    del frame
    global TOWER
    logging.info('Caught {}, shutdown gracefully'.format(signal.strsignal(signum)))
    TOWER.off()
    sys.exit(0)


signal.signal(signal.SIGTERM, exit_gracefully)
signal.signal(signal.SIGINT, exit_gracefully)


def current_cpu_temperature():
    return psutil.sensors_temperatures()['cpu_thermal'][0].current


def count_percentage(values: Sequence, comparator: Callable):
    suitable = list(filter(comparator, values))
    return len(suitable) / len(values) * 100


class IceTower(gpiozero.OutputDevice):

    def __init__(self, pin: int):
        super(IceTower, self).__init__(pin, initial_value=None)

    def on(self):
        logging.info('ON ice tower')
        super(IceTower, self).on()

    def off(self):
        logging.info('OFF ice tower')
        super(IceTower, self).off()


def parse_args(args: list) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='Switch on/off ice tower',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('pin',
                        help='Num of gpio pin',
                        type=int,
                        choices=AVAILABLE_GPIO_PINS)
    parser.add_argument('-d', '--delay',
                        dest='delay',
                        help='Delay between measurements (seconds)',
                        type=int,
                        default=1)
    parser.add_argument('-t', '--temperature',
                        dest='temperature',
                        help='Temperature limit (celsius degress)',
                        type=float,
                        default=40)
    parser.add_argument('-w', '--window',
                        dest='window',
                        help='Measurements window',
                        type=int,
                        default=10)
    parser.add_argument('-p', '--percentage',
                        dest='percentage',
                        help='Percentage of change',
                        type=float,
                        default=80.0)
    return parser.parse_args(args)


def main(args: dict):
    global TOWER
    tower = IceTower(args['pin'])
    TOWER = tower
    measurements = deque(maxlen=args['window'])
    while True:
        time.sleep(args['delay'])
        temp = current_cpu_temperature()
        measurements.append(temp)
        logging.info('Current CPU temperature: {}'.format(temp))
        if len(measurements) == args['window']:
            if tower.value == 0:
                actual_percentage = count_percentage(
                    measurements, lambda x: x > args['temperature'])
                if actual_percentage > args['percentage']:
                    tower.on()
            else:
                actual_percentage = count_percentage(
                    measurements, lambda x: x < args['temperature'])
                if actual_percentage > args['percentage']:
                    tower.off()


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    main(vars(args))
