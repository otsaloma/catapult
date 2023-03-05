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

__version__ = "0.6"

import gi
import logging
import os
import sys

gi.require_version("Gdk", "4.0")
gi.require_version("Gio", "2.0")
gi.require_version("GObject", "2.0")
gi.require_version("Gtk", "4.0")
gi.require_version("Pango", "1.0")

from gi.repository import GLib
from pathlib import Path

CONFIG_HOME = Path(GLib.get_user_config_dir()) / "catapult"
DATA_HOME = Path(GLib.get_user_data_dir()) / "catapult"

# Default to the source directory, overwritten when installing.
DATA_DIR = Path(__file__).parent.parent.joinpath("data").resolve()
LOCALE_DIR = Path(__file__).parent.parent.joinpath("locale").resolve()

# In order of priority for loading plugins and themes.
DATA_DIRS = [DATA_DIR, DATA_HOME, Path("/usr/local/share/catapult")]

# DEBUG will be properly set in Application when arguments are parsed,
# but some debug prints will need the value to be set already before that.
DEBUG = "--debug" in sys.argv[1:]

WAYLAND = (os.getenv("XDG_SESSION_TYPE", "") == "wayland" or
           os.getenv("WAYLAND_DISPLAY", ""))

from catapult import i18n # noqa
from catapult import util # noqa
from catapult.mixins import DebugMixin # noqa
from catapult.conf import ConfigurationStore # noqa
from catapult.conf import PluginConfigurationStore # noqa
conf = ConfigurationStore()
from catapult.preferences import PreferencesItem # noqa
from catapult.plugin import Plugin # noqa
from catapult import plugins # noqa
from catapult.history import History # noqa
from catapult.search import SearchManager # noqa
from catapult.search import SearchResult # noqa
from catapult.about import AboutDialog # noqa
from catapult.preferences import PreferencesDialog # noqa
from catapult.window import Window # noqa
from catapult.app import Application # noqa


def init_logging():
    level = logging.DEBUG if DEBUG else logging.INFO
    path = DATA_HOME / "catapult.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    f = logging.FileHandler(path, mode="w", encoding="utf-8")
    logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s",
                        datefmt="%H:%M:%S",
                        level=level,
                        handlers=[logging.StreamHandler(), f])

def main(args):
    global app
    init_logging()
    conf.read()
    i18n.bind()
    app = Application(args)
    raise SystemExit(app.run())
