# -*- coding: utf-8 -*-

# Copyright (C) 2021 Osmo Salomaa
# Copyright (C) 2015 Aleksandr Gornostal
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

from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Keybinder


class Window(Gtk.ApplicationWindow):

    def __init__(self):
        GObject.GObject.__init__(self)
        self._body = None
        self._input_entry = None
        self._toggle_key = None
        self._init_properties()
        self._init_visual()
        self._init_widgets()
        self._init_position()
        self._init_css_classes()
        self._init_css()
        self._init_signal_handlers()
        self._init_keys()

    def _init_css(self):
        css = catapult.util.load_theme(catapult.conf.theme)
        provider = Gtk.CssProvider()
        provider.load_from_data(bytes(css.encode()))
        style = self.get_style_context()
        screen = Gdk.Screen.get_default()
        priority = Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        style.add_provider_for_screen(screen, provider, priority)

    def _init_css_classes(self):
        self._body.get_style_context().add_class("catapult-body")
        self._input_entry.get_style_context().add_class("catapult-input")

    def _init_keys(self):
        Keybinder.init()
        GLib.idle_add(self.bind_toggle_key, catapult.conf.toggle_key)

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
        self.set_default_size(600, -1)
        self.set_keep_above(True)
        self.set_resizable(False)
        self.set_skip_pager_hint(True)
        self.set_skip_taskbar_hint(True)

    def _init_signal_handlers(self):
        self._input_entry.connect("key-press-event", self._on_input_entry_key_press_event)

    def _init_visual(self):
        # Make window transparent to allow rounded corners.
        screen = Gdk.Screen.get_default()
        visual = screen.get_rgba_visual()
        if not visual: return
        self.set_app_paintable(True)
        self.set_visual(visual)

    def _init_widgets(self):
        self._input_entry = Gtk.Entry()
        self._body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._body.pack_start(self._input_entry, expand=True, fill=True, padding=0)
        self._body.show_all()
        self.add(self._body)

    def bind_toggle_key(self, key):
        self.unbind_toggle_key()
        Keybinder.bind(key, self.toggle)
        self._toggle_key = key

    def get_query(self):
        return self._input_entry.get_text().lower().strip()

    def _on_input_entry_key_press_event(self, entry, event):
        if event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            if self.get_query() in ["q", "quit"]:
                return self.destroy()
        if event.keyval == Gdk.KEY_Escape:
            return self.hide()

    def show(self):
        self._input_entry.set_text("")
        self._input_entry.grab_focus()
        super().show()

    def toggle(self, *args, **kwargs):
        self.hide() if self.is_visible() else self.show()

    def unbind_toggle_key(self):
        if not self._toggle_key: return
        Keybinder.unbind(self._toggle_key)
        self._toggle_key = None
