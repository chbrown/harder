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
    original_label = r.get(ns(opts.host, 'label'))
    # but even then, we don't use it if it already exists
    for i in range(100):
        if i == 0:
            label = original_label
        else:
            # increment label
            label = '%s-%02d' % (original_label, i)

        destination = os.path.join(opts.destination, label)
        if not os.path.exists(destination):
            # success!
            if label != original_label:
                # publish a change if we ended up having to change the value
                label = r.set(ns(opts.host, 'label'), label)
                r.publish(ns(opts.host, 'action'), 'change')
            break
    else:
        raise Exception('No available paths found')

    # mount
    r.publish(ns(opts.host, 'action'), 'mounting')
    mount_point = mkdir_p('/mnt/sr0')
    subprocess.call(['mount', '/dev/sr0', mount_point])

    # copy
    wd = os.getcwd()
    os.chdir(mount_point)
    progress = -1
    filenames = list(walk('.'))
    total = len(filenames)
    r.publish(ns(opts.host, 'action'), 'found %d files' % total)
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

    # change dir back to original so that we can unmount
    os.chdir(wd)
    logger.info('done; cd %s', wd)
    r.publish(ns(opts.host, 'action'), 'done')


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
        # import pyudev
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
