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

from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import Gtk


class Window(Gtk.ApplicationWindow):

    def __init__(self):
        GObject.GObject.__init__(self)
        self._input_entry = None
        self._init_properties()
        self._init_widgets()
        self._init_position()

    def _init_position(self):
        window_width, window_height = self.get_size()
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor()
        rect = monitor.get_geometry()
        screen_width, screen_height = rect.width, rect.height
        x = int(0.50 * (screen_width - window_width))
        y = int(0.25 * (screen_height - window_height))
        self.move(x, y)

    def _init_properties(self):
        self.set_icon_name("io.otsaloma.catapult")
        Gtk.Window.set_default_icon_name("io.otsaloma.catapult")
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_resizable(False)
        self.set_skip_pager_hint(True)
        self.set_skip_taskbar_hint(True)

    def _init_widgets(self):
        self._input_entry = Gtk.Entry()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.pack_start(self._input_entry, expand=True, fill=True, padding=0)
        box.show_all()
        self.add(box)
