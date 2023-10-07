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
import inspect
import logging

from catapult.i18n import _
from gi.repository import GObject
from gi.repository import Gtk

class PreferencesItem:

    def __init__(self, conf=None, parent=None):
        self.conf = conf
        self.parent = parent
        self.label = None
        self.widget = None

    def dump(self, window):
        pass

    def load(self, window):
        pass

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

class TogglePlugin(PreferencesItem):

    def __init__(self, plugin, title):
        self._connected_items = []
        self.label = Gtk.Label(label=_("{} plugin").format(title))
        self.plugin = plugin
        self.widget = Gtk.Switch()
        self.widget.connect("notify::active", self._on_widget_notify_active)

    def connect_items(self, items):
        self._connected_items = list(items)
        self.update_sensitivities()

    def dump(self, window):
        active = self.plugin in catapult.conf.plugins
        self.widget.set_active(active)

    def load(self, window):
        active = self.widget.get_active()
        self.set_plugin_active(window, self.plugin, active)

    def _on_widget_notify_active(self, *args, **kwargs):
        self.update_sensitivities()

    def set_plugin_active(self, window, plugin, active):
        if active:
            catapult.conf.plugins.append(plugin)
        elif plugin in catapult.conf.plugins:
            catapult.conf.plugins.remove(plugin)
        catapult.conf.plugins = sorted(set(catapult.conf.plugins))
        window.set_plugin_active(plugin, active)

    def update_sensitivities(self):
        active = self.widget.get_active()
        for item in self._connected_items:
            item.label.set_sensitive(active)
            item.widget.set_sensitive(active)

class PreferencesDialog(Gtk.Dialog, catapult.DebugMixin):

    def __init__(self, window):
        GObject.GObject.__init__(self, use_header_bar=True)
        self.items = []
        self.main_window = window
        self.set_default_size(-1, 400)
        self.set_title(_("Preferences"))
        stack = Gtk.Stack()
        stack.set_vhomogeneous(True)
        sidebar = Gtk.StackSidebar()
        sidebar.set_stack(stack)
        sidebar.set_vexpand(True)
        sidebar.add_css_class("catapult-preferences-sidebar")
        page = self.get_page([Theme])
        stack.add_titled(page, "general", _("General"))
        for name in self.list_plugins():
            try:
                cls = catapult.util.load_plugin_class(name)
                cls.ensure_configuration()
                toggle = TogglePlugin(name, cls.title)
                preferences_items = [x(conf=cls.conf, parent=self) for x in cls.preferences_items]
                toggle.connect_items(preferences_items)
                page = self.get_page([toggle] + preferences_items)
                stack.add_titled(page, name, cls.title)
            except Exception:
                logging.exception(f"Failed to load configuration for {name}")
        content = self.get_child()
        content.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        grid = Gtk.Grid()
        grid.attach(sidebar, 0, 0, 1, 1)
        grid.attach(stack, 1, 0, 1, 1)
        content.append(grid)
        self.show()

    def get_page(self, items):
        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.set_column_spacing(18)
        grid.set_margin_bottom(18)
        grid.set_margin_end(18)
        grid.set_margin_start(18)
        grid.set_margin_top(18)
        grid.set_row_spacing(12)
        for i, item in enumerate(items):
            if inspect.isclass(item):
                item = item()
            item.dump(self.main_window)
            item.label.set_xalign(1)
            item.label.add_css_class("dim-label")
            grid.attach(item.label, 0, i, 1, 1)
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
            box.append(item.widget)
            grid.attach(box, 1, i, 2, 1)
            self.items.append(item)
        return grid

    def list_plugins(self):
        yield from ["apps", "session", "files", "calculator", "clipboard"]
        for name, module in catapult.util.list_custom_plugins():
            yield name

    def load(self, window):
        # Load toggles last, since deactivating a plugin will trigger writing
        # the configuration to file and that should be done only after all the
        # actual configuration values are loaded.
        for item in sorted(self.items, key=lambda x: isinstance(x, TogglePlugin)):
            name = ".".join((item.__class__.__module__, item.__class__.__name__))
            self.debug(f"Loading configuration from {name}")
            item.load(window)
