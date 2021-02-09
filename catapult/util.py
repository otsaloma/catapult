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
import importlib
import inspect
import os


def find_plugin(name):
    for candidate, module in list_plugins():
        if candidate == name:
            return module

def find_theme(name):
    for candidate, path in list_themes():
        if candidate == name:
            return path

def get_data_path(*paths):
    return os.path.join(catapult.DATA_DIR, *paths)

def list_plugins():
    found = set()
    for name, module in inspect.getmembers(
            catapult.plugins, inspect.ismodule):
        if name in found: continue
        yield name, module
        found.add(name)
    for data_directory in catapult.DATA_DIRS:
        directory = os.path.join(data_directory, "plugins")
        if not os.path.isdir(directory): continue
        for fname in os.listdir(directory):
            if not fname.endswith(".py"): continue
            name = fname.rsplit(".", maxsplit=1)[0]
            if name in found: continue
            yield name, os.path.join(directory, fname)
            found.add(name)

def list_themes():
    found = set()
    for data_directory in catapult.DATA_DIRS:
        directory = os.path.join(data_directory, "themes")
        if not os.path.isdir(directory): continue
        for fname in os.listdir(directory):
            if not fname.endswith(".css"): continue
            name = fname.rsplit(".", maxsplit=1)[0]
            if name in found: continue
            yield name, os.path.join(directory, fname)
            found.add(name)

def load_plugin(name):
    module = find_plugin(name)
    if not inspect.ismodule(module):
        loader = importlib.machinery.SourceFileLoader(name, module)
        module = loader.load_module(name)
    for name, cls in inspect.getmembers(
            module, lambda x: (
                inspect.isclass(x) and
                issubclass(x, catapult.Plugin))):
        return cls()

def load_theme(name):
    path = find_theme(name)
    with open(path, "r") as f:
        return f.read().replace("@input-font", catapult.conf.input_font)
