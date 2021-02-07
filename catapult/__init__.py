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

__version__ = "0.0.1"

import gi
gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")

from catapult.paths import CONFIG_HOME_DIR # noqa
from catapult.paths import DATA_DIR # noqa
from catapult.paths import DATA_DIRS # noqa
from catapult.paths import DATA_HOME_DIR # noqa
from catapult.conf import ConfigurationStore # noqa
from catapult import util # noqa
from catapult.window import Window # noqa
from catapult.app import Application # noqa


def main(args):
    global app, conf
    conf = ConfigurationStore()
    conf.read()
    app = Application(args)
    raise SystemExit(app.run())
