# Copyright (C) oVirt Developers <devel@ovirt.org>
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
import os
import subprocess

from . import backend
from . import errors
from . import osutil

log = logging.getLogger("userstorage")

DEFAULT_UID = 0
DEFAULT_GID = 6


class LoopDevice(backend.Base):
    """
    A loop device with optionally specific sector size.
    """

    _have_sector_size = None

    def __init__(self, base_dir, name, size, sector_size=512, required=True):
        self.base_dir = base_dir
        self.name = name
        self.size = size
        self.sector_size = sector_size
        self.required = required
        self.path = os.path.join(base_dir, name + "-loop")
        self._backing = os.path.join(base_dir, name + "-backing")

    # Backend interface

    def create(self):
        if self.sector_size == 4096 and not self.have_sector_size():
            raise errors.Unsupported(
                "Sector size {} not supported" .format(self.sector_size))

        if self.exists():
            log.debug("Reusing loop device %s", self.path)
            return

        log.info("Creating backing file %s", self._backing)
        with open(self._backing, "w") as f:
            f.truncate(self.size)

        log.info("Creating loop device %s", self.path)
        try:
            device = self._create_loop_device()
        except subprocess.CalledProcessError as e:
            # Creating loop devices using --sector-size is flaky on some setups
            # like oVirt CI, running in under mock.
            raise errors.CreateFailed(
                "Error creating loop device: {}".format(e))

        if os.geteuid() != 0:
            osutil.chown(device, os.geteuid(), os.getegid())

        # Remove stale symlink.
        if os.path.islink(self.path):
            os.unlink(self.path)

        os.symlink(device, self.path)

    def delete(self):
        log.info("Removing loop device %s", self.path)

        if self.exists():
            device = os.path.realpath(self.path)
            osutil.chown(device, DEFAULT_UID, DEFAULT_GID)
            self._remove_loop_device()

        osutil.remove_file(self.path)

        log.info("Removing backing file %s", self._backing)
        osutil.remove_file(self._backing)

    def exists(self):
        return os.path.exists(self.path)

    def setup(self):
        subprocess.check_call(["blkdiscard", self.path])

    # LoopDevice interface.

    @classmethod
    def have_sector_size(cls):
        if cls._have_sector_size is None:
            out = subprocess.check_output(["losetup", "-h"]).decode()
            cls._have_sector_size = "--sector-size <num>" in out
        return cls._have_sector_size

    # Helpers

    def _create_loop_device(self):
        cmd = ["sudo", "losetup", "--find", self._backing, "--show"]

        if self.sector_size != 512:
            cmd.append("--sector-size")
            cmd.append(str(self.sector_size))

        out = subprocess.check_output(cmd)
        return out.decode("utf-8").strip()

    def _remove_loop_device(self):
        subprocess.check_call(["sudo", "losetup", "-d", self.path])
