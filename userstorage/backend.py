# Copyright (C) 2019 Nir Soffer
# This program is free software; see LICENSE for more info.

from __future__ import absolute_import
from __future__ import division


class Error(Exception):
    """
    Base class for backend errors.
    """


class Unsupported(Error):
    """
    May be raised in setup() if backend is not supported on the current system.
    """


class SetupFailed(Error):
    """
    May be raised in setup() if backend should be supported but setup has
    failed.
    """


class Base(object):
    """
    Base class for backend objects.
    """

    # Name used by the tests to locate this backend. Storage backends must be
    # configured with a unique name.
    name = None

    # Storage logical block size.
    sector_size = 512

    # Path to backend. This can be a regular file, a directory, a block device,
    # or a symlink, depending on the backend.
    path = None

    # Set to False to ignore setup errors. Tests using this storage will handle
    # the missing storage.
    required = True

    def setup(self):
        """
        Set up backend for testing.
        """
        raise NotImplementedError

    def teardown(self):
        """
        Clean up backend when it not needed any more.
        """
        raise NotImplementedError

    def exists(self):
        """
        Return True if backend is set up and can be used.
        """
        raise NotImplementedError

    def __str__(self):
        return self.name
