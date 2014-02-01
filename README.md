# harder

`harder` copies soft media, like CDs and DVDs, to your hard drive.

**Goals**:

- minimal user input
- autodetect cd/dvd changes
- prioritize expediency and resiliency over disk space efficiency


## Usage

`harder --destination `

**System configuration**:

Install `harder`, and find out where your system Python put it:

    which harder
    > /usr/local/bin/harder

Using [this page](http://confoundedtech.blogspot.com/2012/12/ubuntu-1204-run-custom-command-on-cd.html) as a starting point:

    cd /etc/udev/rules.d

We need to create a new file in this folder that runs before the others:

    sudo vim 10-harder.rules

Insert the following text:

    KERNEL=="sr[0-9]", ACTION=="change", ENV{ID_CDROM_MEDIA_CD}=="1", RUN+="/usr/local/bin/harder --type cd --destination /backups/harder"
    KERNEL=="sr[0-9]", ACTION=="change", ENV{ID_CDROM_MEDIA_TRACK_COUNT_AUDIO}=="1", RUN+="/usr/local/bin/harder --type cda --destination /backups/harder"
    KERNEL=="sr[0-9]", ACTION=="change", ENV{ID_CDROM_MEDIA_DVD}=="1", RUN+="/usr/local/bin/harder --type dvd --destination /backups/harder"

It seems the following `ENV{ID_CDROM_???}` boolean variables will be available:

  - `ID_CDROM_MEDIA_BD`: Blu-ray
  - `ID_CDROM_MEDIA_DVD`: DVD
  - `ID_CDROM_MEDIA_CD`: CD
  - `ID_CDROM_MEDIA_TRACK_COUNT_AUDIO`: AUDIO CD


## References

- [Writing udev rules](http://www.reactivated.net/writing_udev_rules.html)

http://salt.readthedocs.org/en/latest/ref/states/all/salt.states.supervisord.html
http://salt.readthedocs.org/en/latest/ref/modules/all/salt.modules.supervisord.html


## Installation

**From github:**

```sh
git clone https://github.com/chbrown/harder.git
cd harder
python setup.py develop
```

**Import:**

```python
import harder
```


## License

Copyright © 2014 Christopher Brown. [MIT Licensed](LICENSE).
