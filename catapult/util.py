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
import re

from gi.repository import Gdk
from gi.repository import Gtk
from pathlib import Path


def copy_text_to_clipboard(text):
    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    clipboard.set_text(text, -1)
    clipboard.store()

def find_plugin(name):
    for candidate, module in list_plugins():
        if candidate == name:
            return module

def find_theme(name):
    for candidate, path in list_themes():
        if candidate == name:
            return path

def get_desktop_environment():
    return os.getenv("XDG_CURRENT_DESKTOP", "")

def get_screen_size():
    display = Gdk.Display.get_default()
    monitor = display.get_primary_monitor()
    rect = monitor.get_geometry()
    return rect.width, rect.height

def is_path(location):
    return Path(location).is_absolute()

def is_uri(location):
    return re.match(r"^[a-z]+://", location) is not None

def iterate_main():
    while Gtk.events_pending():
        Gtk.main_iteration()

def list_plugins():
    found = set()
    for name, module in inspect.getmembers(
            catapult.plugins, inspect.ismodule):
        if name in found: continue
        yield name, module
        found.add(name)
    for data_directory in catapult.DATA_DIRS:
        directory = data_directory / "plugins"
        if not directory.exists(): continue
        for fname in directory.glob("*.py"):
            if fname.stem in found: continue
            yield fname.stem, fname.resolve()
            found.add(fname.stem)

def list_themes():
    found = set()
    for data_directory in catapult.DATA_DIRS:
        directory = data_directory / "themes"
        if not directory.exists(): continue
        for fname in directory.glob("*.css"):
            if fname.stem in found: continue
            yield fname.stem, fname.resolve()
            found.add(fname.stem)

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
    css = find_theme(name).read_text()
    for name, path in list_themes():
        # Change import references to absolute paths.
        css = css.replace(f"@{name}@", str(path))
    return css

def lookup_icon(*names):
    theme = Gtk.IconTheme.get_default()
    all_names = set(theme.list_icons())
    for name in names:
        if name in all_names:
            return name
