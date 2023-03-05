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
import logging

from argparse import ArgumentParser
from catapult.i18n import _
from gi.repository import Gio
from gi.repository import GObject
from gi.repository import Gtk


class Application(Gtk.Application):

    def __init__(self, args):
        GObject.GObject.__init__(self)
        self.set_application_id("io.otsaloma.catapult")
        self.set_flags(Gio.ApplicationFlags.FLAGS_NONE)
        self.connect("activate", self._on_activate, args)

    def _on_activate(self, app, args):
        if self.get_windows():
            # If already running, show the existing window.
            return self.get_active_window().show()
        args = self._parse_arguments(args)
        window = catapult.Window()
        self.add_window(window)
        if args.show:
            window.show()
        logging.info(_("Catapult ready"))

    def _parse_arguments(self, args):
        parser = ArgumentParser(usage=_("catapult [OPTION...]"))
        parser.add_argument("--debug",
                            action="store_true",
                            dest="debug",
                            default=False,
                            help=_("print details of indexing and search results"))

        parser.add_argument("--show",
                            action="store_true",
                            dest="show",
                            default=False,
                            help=_("show window immediately"))

        parser.add_argument("--version",
                            action="version",
                            version=f"catapult {catapult.__version__}")

        args = parser.parse_args()
        catapult.DEBUG = args.debug
        if catapult.DEBUG:
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)
        return args
