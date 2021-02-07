# -*- coding: utf-8 -*-

# Copyright (C) 2021 Osmo Salomaa
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import os


def get_config_home_directory_xdg():
    directory = os.path.join(os.path.expanduser("~"), ".config")
    directory = os.environ.get("XDG_CONFIG_HOME", directory)
    directory = os.path.join(directory, "catapult")
    return os.path.abspath(directory)

def get_data_home_directory_xdg():
    directory = os.path.join(os.path.expanduser("~"), ".local", "share")
    directory = os.environ.get("XDG_DATA_HOME", directory)
    directory = os.path.join(directory, "catapult")
    return os.path.abspath(directory)

def get_data_directory_source():
    directory = os.path.dirname(os.path.abspath(__file__))
    directory = os.path.abspath(os.path.join(directory, ".."))
    directory = os.path.join(directory, "data")
    return os.path.abspath(directory)

CONFIG_HOME_DIR = get_config_home_directory_xdg()
DATA_DIR = get_data_directory_source()
DATA_HOME_DIR = get_data_home_directory_xdg()
DATA_LOCAL_DIR = None

# In order of priority so that themes etc. can be overridden.
DATA_DIRS = [DATA_HOME_DIR, DATA_LOCAL_DIR, DATA_DIR]
DATA_DIRS = list(filter(None, DATA_DIRS))
