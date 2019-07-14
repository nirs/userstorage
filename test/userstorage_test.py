# Copyright (C) 2019 Nir Soffer
# This program is free software; see LICENSE for more info.

from __future__ import absolute_import
from __future__ import division

import errno
import glob
import io
import mmap
import os
import shutil
import stat
import subprocess

from contextlib import closing

import pytest

import userstorage

BACKENDS = userstorage.load_config("exampleconf.py").BACKENDS


@pytest.fixture(
    params=[
        BACKENDS["block-512"],
        BACKENDS["block-4k"],
    ],
    ids=str,
)
def user_loop(request):
    backend = validate_backend(request.param)
    yield backend

    # Discard loop device to ensure next test is not affected.
    # TODO: Should be implemented by backend.

    subprocess.check_output(["blkdiscard", backend.path])


@pytest.fixture(
    params=[
        BACKENDS["mount-512"],
        BACKENDS["mount-4k"]
    ],
    ids=str,
)
def user_mount(request):
    backend = validate_backend(request.param)
    yield backend

    # Remove files and directories created by the current tests to ensure that
    # the next test is not affected.
    # TODO: Should be implemented by backend.

    for path in glob.glob(os.path.join(backend.path, "*")):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)


@pytest.fixture(
    params=[
        BACKENDS["file-512"],
        BACKENDS["file-4k"],
    ],
    ids=str,
)
def user_file(request):
    backend = validate_backend(request.param)
    yield backend

    # Truncate file to ensure that next test is not affected.
    # TODO: Should be implemented by backend.

    with open(backend.path, "w") as f:
        f.truncate(0)


def validate_backend(backend):
    if not backend.exists():
        pytest.xfail("backend {} not available".format(backend))
    return backend


def test_loop_device(user_loop):
    assert is_block_device(user_loop.path)
    assert logical_block_size(user_loop.path) == user_loop.sector_size


def test_mount(user_mount):
    assert os.path.isdir(user_mount.path)

    filename = os.path.join(user_mount.path, "file")
    with open(filename, "w") as f:
        f.truncate(4096)

    assert detect_block_size(filename) == user_mount.sector_size


def test_file(user_file):
    assert os.path.isfile(user_file.path)
    assert detect_block_size(user_file.path) == user_file.sector_size


def is_block_device(path):
    mode = os.stat(path).st_mode
    return stat.S_ISBLK(mode)


def logical_block_size(path):
    realpath = os.path.realpath(path)
    dev = os.path.split(realpath)[1]
    lbs = "/sys/block/{}/queue/logical_block_size".format(dev)
    with open(lbs) as f:
        return int(f.readline())


def detect_block_size(path):
    """
    Detect the minimal block size for direct I/O. This is typically the sector
    size of the underlying storage.

    Copied from ovirt-imageio.
    """
    fd = os.open(path, os.O_RDONLY | os.O_DIRECT)
    with io.FileIO(fd, "r") as f:
        for block_size in (512, 4096):
            buf = mmap.mmap(-1, block_size)
            with closing(buf):
                try:
                    f.readinto(buf)
                except EnvironmentError as e:
                    if e.errno != errno.EINVAL:
                        raise
                else:
                    return block_size
        raise RuntimeError("Cannot detect block size")
