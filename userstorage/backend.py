# Copyright (C) oVirt Developers <devel@ovirt.org>
# SPDX-License-Identifier: GPL-2.0-or-later


class Base(object):
    """
    Base class for backend objects. Can be used as a context manager.
    """

    # Name used by the tests to locate this backend. Storage backends must be
    # configured with a unique name.
    name = ""

    # Storage logical block size.
    sector_size = 512

    # Path to backend. This can be a regular file, a directory, a block device,
    # or a symlink, depending on the backend.
    path = None

    # Set to False to ignore setup errors. Tests using this storage will handle
    # the missing storage.
    required = True

    # Provisioning storage.

    def create(self):
        """
        Create storage backend.
        """
        raise NotImplementedError

    def delete(self):
        """
        Delete storage backend.
        """
        raise NotImplementedError

    def exists(self):
        """
        Return True if backend was created and can be used in a test.
        """
        raise NotImplementedError

    # Ensuring test isolation.

    def setup(self):
        """
        Should be called before each test to ensure old data from previous
        tests does not break this test.

        Should be called in your pytest fixture before yielding the backend to
        the tests. If you use unittest based tests, should be called in
        setUp().

        Subclass should override if needed.
        """

    def teardown(self):
        """
        Should be called after each test if cleanup is needed.

        Should be called in your pytest fixture after yielding the the backed
        to the tests. If you use unittest based tests, should be called in
        tearDown().

        Subclass should override if needed.
        """

    def __enter__(self):
        """
        Setup the current storage and return it. Invokes
        userstorage.missing_handler() if storage does not exist.
        """
        if not self.exists():
            from . import missing_handler
            missing_handler(f"backend {self} does not exist")
        self.setup()
        return self

    def __exit__(self, *args):
        """
        Cleanup current storage on context exit.
        """
        self.teardown()

    # Displaying.

    def __str__(self):
        return self.name
