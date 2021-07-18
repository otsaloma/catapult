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
import itertools

from catapult.i18n import _
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import Gtk


class PreferencesItem:

    def __init__(self):
        self.label = None
        self.widget = None

    def dump(self, window):
        pass

    def load(self, window):
        pass

    def set_plugin_active(self, window, plugin, active):
        if active:
            catapult.conf.plugins.append(plugin)
        elif plugin in catapult.conf.plugins:
            catapult.conf.plugins.remove(plugin)
        catapult.conf.plugins = sorted(set(catapult.conf.plugins))
        window.set_plugin_active(plugin, active)


class Theme(PreferencesItem):

    def __init__(self):
        self.label = Gtk.Label(label=_("Theme"))
        self.widget = Gtk.ComboBoxText()
        themes = catapult.util.list_themes()
        self.themes = sorted(x[0] for x in themes)
        for name in self.themes:
            self.widget.append_text(name)

    def dump(self, window):
        if catapult.conf.theme not in self.themes: return
        index = self.themes.index(catapult.conf.theme)
        self.widget.set_active(index)

    def load(self, window):
        theme = self.widget.get_active_text()
        if not theme in self.themes: return
        catapult.conf.theme = theme
        window.load_css()


class ToggleKey(PreferencesItem):

    def __init__(self):
        self.label = Gtk.Label(label=_("Activation key"))
        self.widget = Gtk.Entry()
        self.widget.catapult_key = None
        self.widget.connect("key-press-event", self._on_key_press_event)

    def dump(self, window):
        keyval, mods = Gtk.accelerator_parse(catapult.conf.toggle_key)
        label = Gtk.accelerator_get_label(keyval, mods)
        self.widget.catapult_key = catapult.conf.toggle_key
        self.widget.set_text(label)
        self.widget.set_position(-1)
        if window is not None:
            # Avoid the main window popping up.
            window.unbind_toggle_key()

    def load(self, window):
        key = self.widget.catapult_key
        success = window.bind_toggle_key(key)
        if not success: return
        catapult.conf.toggle_key = key

    def _on_key_press_event(self, widget, event):
        if event.keyval in [Gdk.KEY_Tab, Gdk.KEY_Escape]:
            return False
        if event.keyval in [Gdk.KEY_BackSpace, Gdk.KEY_Delete]:
            self.dump(None)
            return True
        mods = event.state
        # Allow Mod1, which is usually Alt, remove the rest.
        # https://mail.gnome.org/archives/gtk-list/2001-July/msg00153.html
        for bad in [Gdk.ModifierType.MOD2_MASK,
                    Gdk.ModifierType.MOD3_MASK,
                    Gdk.ModifierType.MOD4_MASK,
                    Gdk.ModifierType.MOD5_MASK]:
            if mods & bad:
                mods ^= bad
        key = Gtk.accelerator_name(event.keyval, mods)
        label = Gtk.accelerator_get_label(event.keyval, mods)
        self.widget.catapult_key = key
        self.widget.set_text(label)
        self.widget.set_position(-1)
        return True


class CustomPlugin(PreferencesItem):

    def __init__(self, plugin):
        title = plugin.replace("_", " ").title()
        self.label = Gtk.Label(label=_("{} plugin").format(title))
        self.plugin = plugin
        self.widget = Gtk.Switch()

    def dump(self, window):
        active = self.plugin in catapult.conf.plugins
        self.widget.set_active(active)

    def load(self, window):
        active = self.widget.get_active()
        self.set_plugin_active(window, self.plugin, active)


class PreferencesDialog(Gtk.Dialog, catapult.DebugMixin, catapult.WindowMixin):

    def __init__(self, window):
        GObject.GObject.__init__(self)
        self.items = []
        self.set_border_width(18)
        self.set_title(_("Preferences"))
        grid = Gtk.Grid()
        grid.set_column_spacing(18)
        grid.set_row_spacing(12)
        items = [x() for x in self.get_items()]
        # Add switches for all custom plugins found.
        # TODO: We'll probably eventually want to put these on
        # a separate page of a Gtk.StackSwitcher or something.
        for name, module in catapult.util.list_custom_plugins():
            items.append(CustomPlugin(name))
        for i, item in enumerate(items):
            item.dump(window)
            item.label.set_xalign(1)
            item.label.get_style_context().add_class("dim-label")
            grid.attach(item.label, 0, i, 1, 1)
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
            box.pack_start(item.widget, expand=False, fill=False, padding=0)
            grid.attach(box, 1, i, 1, 1)
            self.items.append(item)
        content = self.get_content_area()
        content.add(grid)
        self.show_all()
        self.set_position_offset(0.5, 0.2)

    def get_items(self):
        yield from itertools.chain(
            [Theme, ToggleKey],
            catapult.util.get_plugin_preferences("apps"),
            catapult.util.get_plugin_preferences("session"),
            catapult.util.get_plugin_preferences("files"),
            catapult.util.get_plugin_preferences("calculator"),
        )

    def load(self, window):
        for item in self.items:
            name = item.__class__.__name__
            self.debug(f"Loading configuration from {name}")
            item.load(window)
