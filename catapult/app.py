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

from gi.repository import Gio
from gi.repository import GObject
from gi.repository import Gtk


class Application(Gtk.Application):

    def __init__(self, args):
        GObject.GObject.__init__(self)
        self.set_application_id("io.otsaloma.catapult")
        self.set_flags(Gio.ApplicationFlags.FLAGS_NONE)
        self.connect("activate", self._on_activate, args)
        self.connect("shutdown", self._on_shutdown)

    def _on_activate(self, app, args):
        window = catapult.Window()
        self.add_window(window)
        window.present()

    def _on_shutdown(self, app):
        # TODO: Write config files etc.
        pass
