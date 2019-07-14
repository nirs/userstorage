# Copyright (C) 2019 Nir Soffer
# This program is free software; see LICENSE for more info.

import errno
import os
import subprocess


def chown(path):
    user_group = "%(USER)s:%(USER)s" % os.environ
    subprocess.check_call(["sudo", "chown", "-R", user_group, path])


def create_dir(path):
    try:
        os.makedirs(path)
    except EnvironmentError as e:
        if e.errno != errno.EEXIST:
            raise


def remove_file(path):
    try:
        os.remove(path)
    except EnvironmentError as e:
        if e.errno != errno.ENOENT:
            raise


def remove_dir(path):
    try:
        os.rmdir(path)
    except EnvironmentError as e:
        if e.errno != errno.ENOENT:
            raise
