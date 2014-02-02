import sys
import argparse
# import threading
# import atexit
import socket
import redis
import pyudev

from harder import tasks
from harder.lib import ns

import logging
logger = logging.getLogger(__name__)


def stderr(s):
    sys.stderr.write(s + '\n')
    sys.stderr.flush()


def make_udev_thread(opts):
    context = pyudev.Context()
    # device = pyudev.Device.from_name(context, 'block', 'sr0')

    r = redis.StrictRedis(host=opts.cc)

    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='block', device_type='disk')
    # monitor.start()

    # for device in iter(monitor.poll, None):
    def callback(device):
        stderr('%s on %s' % (device.action, device.device_path))
        # only report if a label is available (meaning the drive is available)
        # stderr('device.ID_FS_LABEL? = %r' % ('ID_FS_LABEL' in device))
        # set the label & filesystem if it doesn't exist (it's deleted when the drive is ejected)
        ready = tasks.update(opts, device)

        # default to the given action (always 'change', as far as I can tell)
        action = 'ready' if ready else device.action
        r.publish(ns(opts.host, 'action'), action)

    return pyudev.MonitorObserver(monitor, callback=callback)


def task_loop(opts):
    # loop / block while listening for local tasks
    r = redis.StrictRedis(host=opts.cc)
    pubsub = r.pubsub()

    pubsub.subscribe(ns(opts.host, 'task'))
    stderr('pub/sub listening: %s' % ', '.join(pubsub.channels))
    # try:
    for message in pubsub.listen():
        # the first message will be a dummy success message like:
        # {'pattern': None, 'type': 'subscribe', 'channel': 'harder:n004:task', 'data': 1L}
        # real messages will look like:
        # {'pattern': None, 'type': 'message', 'channel': 'harder:n004:task', 'data': 'eject'}
        if message['type'] == 'message':
            task = message['data']
            stderr('performing task: %r' % task)
            task_func = getattr(tasks, task)
            task_func(opts)


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
    udev_thread = make_udev_thread(opts)
    # threading.Thread(target=udev_loop, args=(opts,))
    # udev_thread.daemon = False
    stderr('udev polling starting')
    udev_thread.start()

    try:
        task_loop(opts)
    except (KeyboardInterrupt, SystemExit), exc:
        stderr('task_loop broken: %r' % exc)
    finally:
        udev_thread.stop()
        stderr('udev_loop stopped')

    # @atexit.register
    # def cleanup():
    #     logger.debug('atexit cleanup')


if __name__ == '__main__':
    main()
