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

from catapult.i18n import _
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import Gtk


class PatternEditDialog(Gtk.Dialog):

    def __init__(self, parent, text=""):
        GObject.GObject.__init__(self, use_header_bar=True)
        self.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(_("_OK"), Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.OK)
        self.set_transient_for(parent)
        header = self.get_header_bar()
        header.set_title(_("Edit File Patterns"))
        header.set_subtitle(_("Use shell-style wildcards * and **"))
        self.text_view = Gtk.TextView()
        self.text_view.set_accepts_tab(False)
        self.text_view.set_bottom_margin(6)
        self.text_view.set_left_margin(6)
        self.text_view.set_pixels_below_lines(6)
        self.text_view.set_right_margin(6)
        self.text_view.set_top_margin(6)
        self.text_view.set_wrap_mode(Gtk.WrapMode.NONE)
        self.text_view.get_style_context().add_class("monospace")
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(*((Gtk.PolicyType.AUTOMATIC,)*2))
        scroller.set_shadow_type(Gtk.ShadowType.NONE)
        scroller.set_size_request(600, 371)
        scroller.add(self.text_view)
        content = self.get_content_area()
        content.add(scroller)
        text_buffer = self.text_view.get_buffer()
        text_buffer.set_text(text)
        self.show_all()

    def get_text(self):
        text_buffer = self.text_view.get_buffer()
        start, end = text_buffer.get_bounds()
        return text_buffer.get_text(start, end, False)


class PreferencesItem:

    def __init__(self):
        self.label = None
        self.widget = None

    def dump(self):
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
        self.label = Gtk.Label(_("Theme"))
        self.widget = Gtk.ComboBoxText()
        themes = catapult.util.list_themes()
        self.themes = sorted(x[0] for x in themes)
        for name in self.themes:
            self.widget.append_text(name)

    def dump(self):
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
        self.label = Gtk.Label(_("Activation key"))
        self.widget = Gtk.Entry()
        self.widget.catapult_key = None
        self.widget.connect("key-press-event", self._on_key_press_event)

    def dump(self):
        keyval, mods = Gtk.accelerator_parse(catapult.conf.toggle_key)
        label = Gtk.accelerator_get_label(keyval, mods)
        self.widget.catapult_key = catapult.conf.toggle_key
        self.widget.set_text(label)
        self.widget.set_position(-1)

    def load(self, window):
        key = self.widget.catapult_key
        if key == catapult.conf.toggle_key: return
        success = window.bind_toggle_key(key)
        if not success: return
        catapult.conf.toggle_key = key

    def _on_key_press_event(self, window, event):
        if event.keyval in [Gdk.KEY_Tab, Gdk.KEY_Escape]:
            return False
        if event.keyval in [Gdk.KEY_BackSpace, Gdk.KEY_Delete]:
            self.dump()
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


class Apps(PreferencesItem):

    def __init__(self):
        self.label = Gtk.Label(_("Apps plugin"))
        self.widget = Gtk.Switch()

    def dump(self):
        active = "apps" in catapult.conf.plugins
        self.widget.set_active(active)

    def load(self, window):
        active = self.widget.get_active()
        self.set_plugin_active(window, "apps", active)


class AppsScanInterval(PreferencesItem):

    def __init__(self):
        self.label = Gtk.Label(_("Apps scan interval"))
        self.spin = Gtk.SpinButton()
        self.spin.set_increments(1, 5)
        self.spin.set_range(1, 1440)
        self.unit = Gtk.Label(_("minutes"))
        self.widget = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.widget.pack_start(self.spin, expand=False, fill=False, padding=0)
        self.widget.pack_start(self.unit, expand=False, fill=False, padding=0)

    def dump(self):
        value = catapult.conf.apps_scan_interval
        self.spin.set_value(int(round(value / 60)))

    def load(self, window):
        value = self.spin.get_value_as_int()
        catapult.conf.apps_scan_interval = value * 60


class Session(PreferencesItem):

    def __init__(self):
        self.label = Gtk.Label(_("Session plugin"))
        self.widget = Gtk.Switch()

    def dump(self):
        active = "session" in catapult.conf.plugins
        self.widget.set_active(active)

    def load(self, window):
        active = self.widget.get_active()
        self.set_plugin_active(window, "session", active)


class Files(PreferencesItem):

    def __init__(self):
        self.label = Gtk.Label(_("Files plugin"))
        self.widget = Gtk.Switch()

    def dump(self):
        active = "files" in catapult.conf.plugins
        self.widget.set_active(active)

    def load(self, window):
        active = self.widget.get_active()
        self.set_plugin_active(window, "files", active)


class FilesInclude(PreferencesItem):

    def __init__(self):
        self.label = Gtk.Label(_("Files include patterns"))
        self.widget = Gtk.Button()
        self.widget.set_label(_("Edit"))
        self.widget.connect("clicked", self._on_clicked)

    def _on_clicked(self, *args, **kwargs):
        text = "\n".join(catapult.conf.files_include)
        parent = self.widget.get_ancestor(Gtk.Window)
        dialog = PatternEditDialog(parent, text)
        dialog.connect("response", self._on_response)
        dialog.run()

    def _on_response(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            patterns = dialog.get_text().splitlines()
            patterns = [x.strip() for x in patterns]
            catapult.conf.files_include = patterns
        dialog.destroy()


class FilesExclude(PreferencesItem):

    def __init__(self):
        self.label = Gtk.Label(_("Files exclude patterns"))
        self.widget = Gtk.Button()
        self.widget.set_label(_("Edit"))
        self.widget.connect("clicked", self._on_clicked)

    def _on_clicked(self, *args, **kwargs):
        text = "\n".join(catapult.conf.files_exclude)
        parent = self.widget.get_ancestor(Gtk.Window)
        dialog = PatternEditDialog(parent, text)
        dialog.connect("response", self._on_response)
        dialog.run()

    def _on_response(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            patterns = dialog.get_text().splitlines()
            patterns = [x.strip() for x in patterns]
            catapult.conf.files_exclude = patterns
        dialog.destroy()


class FilesScanInterval(PreferencesItem):

    def __init__(self):
        self.label = Gtk.Label(_("Files scan interval"))
        self.spin = Gtk.SpinButton()
        self.spin.set_increments(1, 5)
        self.spin.set_range(1, 1440)
        self.unit = Gtk.Label(_("minutes"))
        self.widget = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.widget.pack_start(self.spin, expand=False, fill=False, padding=0)
        self.widget.pack_start(self.unit, expand=False, fill=False, padding=0)

    def dump(self):
        value = catapult.conf.files_scan_interval
        self.spin.set_value(int(round(value / 60)))

    def load(self, window):
        value = self.spin.get_value_as_int()
        catapult.conf.files_scan_interval = value * 60


class Calculator(PreferencesItem):

    def __init__(self):
        self.label = Gtk.Label(_("Calculator plugin"))
        self.widget = Gtk.Switch()

    def dump(self):
        active = "calculator" in catapult.conf.plugins
        self.widget.set_active(active)

    def load(self, window):
        active = self.widget.get_active()
        self.set_plugin_active(window, "calculator", active)


class CustomPlugin(PreferencesItem):

    def __init__(self, plugin):
        self.label = Gtk.Label(_("{} plugin").format(plugin.title()))
        self.plugin = plugin
        self.widget = Gtk.Switch()

    def dump(self):
        active = self.plugin in catapult.conf.plugins
        self.widget.set_active(active)

    def load(self, window):
        active = self.widget.get_active()
        self.set_plugin_active(window, self.plugin, active)


class PreferencesDialog(Gtk.Dialog, catapult.DebugMixin):

    ITEMS = [
        Theme,
        ToggleKey,
        Apps,
        AppsScanInterval,
        Session,
        Files,
        FilesInclude,
        FilesExclude,
        FilesScanInterval,
        Calculator,
    ]

    def __init__(self, parent):
        GObject.GObject.__init__(self)
        self.items = []
        self.set_border_width(18)
        self.set_title(_("Preferences"))
        self.set_transient_for(parent)
        grid = Gtk.Grid()
        grid.set_column_spacing(18)
        grid.set_row_spacing(12)
        items = [x() for x in self.ITEMS]
        # Add switches for all custom plugins found.
        # TODO: We'll probably eventually want to put these on
        # a separate page of a Gtk.StackSwitcher or something.
        for name, module in catapult.util.list_custom_plugins():
            items.append(CustomPlugin(name))
        for i, item in enumerate(items):
            item.dump()
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

    def load(self, window):
        for item in self.items:
            name = item.__class__.__name__
            self.debug(f"Loading configuration from {name}")
            item.load(window)
