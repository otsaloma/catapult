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

import catapult
import os


def find_theme(theme):
    for candidate, path in list_themes():
        if candidate == theme:
            return path

def get_data_path(*paths):
    return os.path.join(catapult.DATA_DIR, *paths)

def list_themes():
    found = set()
    for data_directory in catapult.DATA_DIRS:
        directory = os.path.join(data_directory, "themes")
        if not os.path.isdir(directory): continue
        for fname in os.listdir(directory):
            if not fname.endswith(".css"): continue
            theme = fname.rsplit(".", maxsplit=1)[0]
            if theme in found: continue
            yield theme, os.path.join(directory, fname)
            found.add(theme)

def read_theme(theme):
    path = find_theme(theme)
    with open(path, "r") as f:
        return f.read()
