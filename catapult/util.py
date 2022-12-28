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
import functools
import inspect
import os
import re

from gi.repository import Gdk
from gi.repository import Gtk
from importlib.machinery import SourceFileLoader
from pathlib import Path


def atomic_write(path, text, encoding):
    path = path.resolve()
    temp_path = path.with_name(path.name + ".new")
    temp_path.write_text(text, encoding)
    temp_path.replace(path)

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

def get_monitor():
    # No monitor reported as primary by GDK under Wayland
    # https://gitlab.gnome.org/GNOME/gtk/-/issues/1028
    display = Gdk.Display.get_default()
    monitor = display.get_primary_monitor()
    if monitor is not None:
        return monitor
    for i in range(display.get_n_monitors()):
        monitor = display.get_monitor(i)
        if monitor is not None:
            return monitor

def get_screen_size(monitor=None):
    monitor = monitor or get_monitor()
    rect = monitor.get_geometry()
    return rect.width, rect.height

def is_path(location):
    return Path(location).is_absolute()

def is_plugin_class(obj):
    return (inspect.isclass(obj) and
            issubclass(obj, catapult.Plugin) and
            obj is not catapult.Plugin)

def is_uri(location):
    return re.match(r"^[a-z]+://", location) is not None

def iterate_main():
    while Gtk.events_pending():
        Gtk.main_iteration()

def list_custom_plugins():
    for name, module in list_plugins():
        if not inspect.ismodule(module):
            yield name, module

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
        for path in directory.glob("*.py"):
            if path.stem in found: continue
            yield path.stem, path.resolve()
            found.add(path.stem)

def list_themes():
    found = set()
    for data_directory in catapult.DATA_DIRS:
        directory = data_directory / "themes"
        if not directory.exists(): continue
        for path in directory.glob("*.css"):
            if path.stem in found: continue
            yield path.stem, path.resolve()
            found.add(path.stem)

def load_plugin(name):
    return load_plugin_class(name)()

def load_plugin_class(name):
    module = load_plugin_module(name)
    for name, cls in inspect.getmembers(module, is_plugin_class):
        return cls

@functools.lru_cache(1024)
def load_plugin_module(name):
    module = find_plugin(name)
    if inspect.ismodule(module): return module
    loader = SourceFileLoader(name, str(module))
    return loader.load_module(name)

def load_theme(name):
    css = find_theme(name).read_text("utf-8")
    # Allow user to override parts of the theme.
    path = catapult.CONFIG_HOME / "user.css"
    if path.exists():
        css += "\n\n" + path.read_text("utf-8")
    else:
        text = """
/* Any CSS added here can be used to override theme CSS. */
/* Use ":reload-theme" in Catapult to see changes. */
/* For available classes, see the Catapult default "dark" theme: */
/* https://github.com/otsaloma/catapult/blob/master/data/themes/dark.css */"""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text.strip() + "\n", "utf-8")
    for name, path in list_themes():
        # Change import references to absolute paths.
        css = css.replace(f"@{name}@", str(path))
    return css

@functools.lru_cache(256)
def lookup_icon(*names):
    # Note that this does not check if a sufficient size is found,
    # but usually that shouldn't be an issue.
    theme = Gtk.IconTheme.get_default()
    all_names = set(theme.list_icons())
    for name in names:
        if name in all_names:
            return name
