import os
import sys
import argparse
import threading
import socket
import redis
from datetime import datetime
# import time

PREFIX = 'harder:'

import pyudev

# from pprint import pprint
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


def stderr(s):
    sys.stderr.write(s + '\n')
    sys.stderr.flush()


def udev_loop(opts):
    context = pyudev.Context()
    r = redis.StrictRedis(host=opts.cc)

    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='block', device_type='disk')
    monitor.start()

    stderr('udev polling starting')
    for device in iter(monitor.poll, None):
        stderr('%s on %s' % (device.action, device.device_path))
        # device = find_device(DEVNAME='/dev/sr0')
        # device = pyudev.Device.from_name(context, 'block', 'sr0')
        # device = pyudev.Device.from_device_file(context, '/dev/sr0')
        # only report if a label is available (meaning the drive is available)
        stderr('device.ID_FS_LABEL? = %r' % ('ID_FS_LABEL' in device))
        if 'ID_FS_LABEL' in device:
            values = dict(
                action=device.action,
                label=device.get('ID_FS_LABEL'),
                fs_type=device.get('ID_FS_TYPE'),
                devname=device.get('DEVNAME')
            )
            stderr('HMSET %s %r' % (PREFIX + opts.host, values))
            r.hmset(PREFIX + opts.host, values)
            stderr('LPUSH %s %s' % (PREFIX + 'change', opts.host))
            r.lpush(PREFIX + 'change', opts.host)


def task_loop(opts):
    # loop / block while listening for local tasks
    r = redis.StrictRedis(host=opts.cc)

    key = opts.host + ':tasks'
    stderr('looping redis BRPOP %s' % key)
    while True:
        task = r.brpop(key)
        stderr('performing task: %r' % task)


def main():
    parser = argparse.ArgumentParser(description='harder: copy soft media to your hard drive',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', '--destination', help='Destination directory',
        default='/backups/harder')
    parser.add_argument('--host', type=str, help='Hostname of current machine',
        default=socket.gethostname())
    parser.add_argument('--cc', type=str, help='Remote address of UI',
        default='salt')
    parser.add_argument('-v', '--verbose', action='store_true', help='Log extra information')
    # parser.add_argument('-V', '--version', action='version', version=__version__)
    opts = parser.parse_args()

    level = logging.DEBUG if opts.verbose else logging.INFO
    logging.basicConfig(level=level)

    # fork off a thread to watch for udev events
    thread = threading.Thread(target=udev_loop, args=(opts,))
    thread.daemon = True
    thread.start()

    task_loop(opts)

    logger.debug('main is exiting')


if __name__ == '__main__':
    main()
