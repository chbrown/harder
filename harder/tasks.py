import os
import subprocess
import shutil
import pyudev
import redis

from harder.lib import ns

import logging
logger = logging.getLogger(__name__)


def mkdir_p(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    return dirpath


def walk(root):
    # flatten into just all the full filepaths
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            yield os.path.join(dirpath, filename)


def copy(opts):
    # assume it's a normal mountable filesystem, without checking that it's joliet or whatever
    logger.info('copying to %s', opts.destination)

    r = redis.StrictRedis(host=opts.cc)

    # get the label from the database, since it might have been manually set
    label = r.get(ns(opts.host, 'label'))
    destination = os.path.join(opts.destination, label)

    # mount
    r.publish(ns(opts.host, 'action'), 'mounting')
    mount_point = mkdir_p('/mnt/sr0')
    subprocess.call(['mount', '/dev/sr0', mount_point])

    # copy
    os.chdir(mount_point)
    progress = -1
    filenames = list(walk('.'))
    total = len(filenames)
    logger.info('copying %d files', total)
    for i, source_filename in enumerate(filenames):
        source_filepath = os.path.join(mount_point, source_filename)
        target_filepath = os.path.join(destination, source_filename)
        # make sure we can write to where target_filepath needs to be
        mkdir_p(os.path.dirname(target_filepath))
        logger.debug('cp %s %s', source_filepath, target_filepath)
        shutil.copyfile(source_filepath, target_filepath)

        percentage = int(100.0 * i / total)
        if percentage > progress:
            progress = percentage
            r.publish(ns(opts.host, 'action'), '%d%%' % progress)

    r.publish(ns(opts.host, 'action'), 'done')

    # from datetime import datetime
    # timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
    # log_filepath = os.path.join(destination, timestamp + '.log')
    # with open(log_filepath, 'w') as log_fd:
    #     print >> log_fd, 'copying %s to %s' % (media_type, destination)
    #     print >> log_fd, 'ENV'
    #     for env_key, env_value in os.environ.items():
    #         print >> log_fd, '  %s=%s' % (env_key, env_value)


def eject(opts):
    # eject -T doesn't work properly, so we blindly attempt to open the tray, and if that fails, close it
    returncode = subprocess.call(['eject'])
    if returncode != 0:
        subprocess.call(['eject', '-t'])


def update(opts, device=None):
    '''
    Return a boolean representing whether or not the device is ready
    '''
    if device is None:
        context = pyudev.Context()
        device = pyudev.Device.from_device_file(context, '/dev/sr0')

    r = redis.StrictRedis(host=opts.cc)
    r.set(ns(opts.host, 'device'), device['DEVNAME'])
    ready = 'ID_FS_LABEL' in device
    if ready:
        # upgrade the 'change' action to 'ready' if the label is available
        # maybe use r.setnx for both?
        r.set(ns(opts.host, 'label'), device['ID_FS_LABEL'])
        r.set(ns(opts.host, 'filesystem'), device['ID_FS_TYPE'])

    return ready

def reload(opts):
    ready = update(opts)

    r = redis.StrictRedis(host=opts.cc)
    if ready:
        r.publish(ns(opts.host, 'action'), 'ready')
