import os
import argparse
from datetime import datetime

import logging
logger = logging.getLogger(__name__)



def copy(destination, media_type):
    logger.info('copying %s to %s', media_type, destination)

    timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
    log_filepath = os.path.join(destination, timestamp + '.log')

    with open(log_filepath, 'w') as log_fd:
        print >> log_fd, 'copying %s to %s' % (media_type, destination)
        print >> log_fd, 'ENV'
        for env_key, env_value in os.environ.items():
            print >> log_fd, '  %s=%s' % (env_key, env_value)


def main():
    types = set(['cd', 'cda', 'dvd', None])
    parser = argparse.ArgumentParser(description='harder: copy soft media to your hard drive',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', '--destination', default='/backups/harder', help='Destination directory')
    parser.add_argument('-t', '--type', choices=types, help='Type of media inserted')
    parser.add_argument('-v', '--verbose', action='store_true', help='Log extra information')
    # parser.add_argument('-V', '--version', action='version', version=__version__)
    # opts, _ = parser.parse_known_args()
    opts = parser.parse_args()

    level = logging.DEBUG if opts.verbose else logging.INFO
    logging.basicConfig(level=level)

    copy(opts.destination, opts.type)

    logger.debug('success; exiting')


if __name__ == '__main__':
    main()
