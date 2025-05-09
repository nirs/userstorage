# Copyright (C) oVirt Developers <devel@ovirt.org>
# SPDX-License-Identifier: GPL-2.0-or-later

import os
import logging

from . import backend
from . import osutil

log = logging.getLogger("userstorage")


class File(backend.Base):
    """
    A single file on a mounted file system.
    """

    def __init__(self, mount):
        """
        Create file based storage.
        """
        self._mount = mount
        self.path = os.path.join(mount.path, "file")

    # Backend interface.

    @property
    def name(self):
        return self._mount.name

    @property
    def sector_size(self):
        return self._mount.sector_size

    @property
    def required(self):
        return self._mount.required

    def create(self):
        if self.exists():
            log.debug("Reusing file %s", self.path)
            return

        self._mount.create()

        log.info("Creating file %s", self.path)
        open(self.path, "w").close()

    def delete(self):
        log.info("Removing file %s", self.path)
        osutil.remove_file(self.path)
        self._mount.delete()

    def exists(self):
        return os.path.exists(self.path)

    def setup(self):
        open(self.path, "w").close()
