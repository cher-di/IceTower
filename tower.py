import argparse
import logging
import signal
import sys
import time

import gpiozero
import psutil

from collections import deque
from typing import Sequence, Callable

from gpiozero.pins.native import NativeFactory

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s')


AVAILABLE_GPIO_PINS = list(range(2, 28))


def current_cpu_temperature():
    return psutil.sensors_temperatures()['cpu_thermal'][0].current


def count_percentage(values: Sequence, comparator: Callable):
    suitable = list(filter(comparator, values))
    return len(suitable) / len(values) * 100


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
    tower = gpiozero.OutputDevice(args['pin'], pin_factory=NativeFactory)
    measurements = deque(maxlen=args['window'])
    while True:
        time.sleep(args['delay'])
        temp = current_cpu_temperature()
        measurements.append(temp)
        logging.info('Current CPU temperature: {}'.format(temp))
        if tower.value == 0:
            actual_percentage = count_percentage(
                measurements, lambda x: x > args['temperature'])
            if actual_percentage > args['percentage']:
                logging.info('ON ise tower')
                tower.on()
        else:
            actual_percentage = count_percentage(
                measurements, lambda x: x < args['temperature'])
            if actual_percentage > args['percentage']:
                logging.info('OFF ice tower')
                tower.off()


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    main(vars(args))
