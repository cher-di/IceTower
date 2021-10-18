import argparse
import logging
import signal
import sys
import time

import tower_utils

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s')


TOWER = None


def exit_gracefully(signum, frame):
    del frame
    global TOWER
    logging.info('Caught {}, shutdown gracefully'.format(signal.strsignal(signum)))
    TOWER.off()
    sys.exit(0)


signal.signal(signal.SIGTERM, exit_gracefully)
signal.signal(signal.SIGINT, exit_gracefully)


def parse_args(args: list) -> argparse.Namespace:
    parser = argparse.ArgumentParser('Toggle pin with delay')
    parser.add_argument('pin',
                        help='Pin to toggle',
                        type=int,
                        choices=tower_utils.AVAILABLE_GPIO_PINS)
    parser.add_argument('delay',
                        help='Delay in seconds',
                        type=int)
    return parser.parse_args(args)


def main(args: dict):
    global TOWER
    tower = tower_utils.IceTower(args['pin'])
    TOWER = tower

    while True:
        tower.toggle()
        time.sleep(args['delay'])


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    main(vars(args))
