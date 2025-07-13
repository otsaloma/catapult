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

import array
import cairo
import catapult
import itertools
import logging

from catapult import util
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Pango

ICON_SIZE = Gtk.IconSize.LARGE
ICON_SIZE_PX = 48

class SearchResultRow(Gtk.ListBoxRow):

    def __init__(self):
        GObject.GObject.__init__(self)
        self.query = None
        self.result = None
        self.icon = Gtk.Image()
        self.icon.set_pixel_size(ICON_SIZE_PX)
        self.title_label = Gtk.Label()
        self.title_label.set_xalign(0)
        self.title_label.set_yalign(1)
        self.title_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.title_label.set_vexpand(True)
        self.description_label = Gtk.Label()
        self.description_label.set_xalign(0)
        self.description_label.set_yalign(0)
        self.description_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.description_label.set_vexpand(True)
        self.add_css_class("catapult-search-result")
        self.icon.add_css_class("catapult-search-result-icon")
        self.title_label.add_css_class("catapult-search-result-title")
        self.description_label.add_css_class("catapult-search-result-description")
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        hbox.append(self.icon)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        vbox.set_hexpand(True)
        vbox.append(self.title_label)
        vbox.append(self.description_label)
        hbox.append(vbox)
        self.set_child(hbox)

    def set_icon(self, icon, default="application-x-executable"):
        if isinstance(icon, cairo.ImageSurface):
            try:
                # Convert Cairo BGRA to GdkPixbuf RGBA.
                raw = icon.get_data()
                data = array.array("B")
                for i in range(0, len(raw), 4):
                    b, g, r, a = raw[i:i+4]
                    data.extend([r, g, b, a])
                pixbuf = GdkPixbuf.Pixbuf.new_from_data(data=data,
                                                        colorspace=GdkPixbuf.Colorspace.RGB,
                                                        has_alpha=True,
                                                        bits_per_sample=8,
                                                        width=icon.get_width(),
                                                        height=icon.get_height(),
                                                        rowstride=icon.get_stride())

                self.icon.set_from_pixbuf(pixbuf)
            except Exception:
                logging.exception("Failed to set icon from cairo.ImageSurface")
                self.icon.set_from_icon_name(default)
        elif isinstance(icon, Gio.Icon):
            self.icon.set_from_gicon(icon)
        elif isinstance(icon, str) and icon.startswith("<svg"):
            try:
                data = icon.encode("utf-8")
                loader = GdkPixbuf.PixbufLoader.new_with_type("svg")
                scale_factor = self.get_scale_factor()
                size = scale_factor * ICON_SIZE_PX
                loader.set_size(size, size)
                loader.write(data)
                loader.close()
                pixbuf = loader.get_pixbuf()
                self.icon.set_from_pixbuf(pixbuf)
            except Exception:
                logging.exception("Failed to set icon from cairo.ImageSurface")
                self.icon.set_from_icon_name(default)
        elif isinstance(icon, str):
            self.icon.set_from_icon_name(icon)
        self.icon.set_icon_size(Gtk.IconSize.LARGE)

class Window(Gtk.ApplicationWindow, catapult.DebugMixin):

    def __init__(self):
        GObject.GObject.__init__(self)
        self._body = None
        self._css_provider = None
        self._icon_theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        self._icon_theme_handler_id = None
        self._input_entry = Gtk.Entry()
        self._plugins = []
        self._position = (0, 0)
        self._prev_query = ""
        self._result_list = Gtk.ListBox()
        self._result_list_height_set = False
        self._result_rows = []
        self._result_scroller = Gtk.ScrolledWindow()
        self._search_manager = catapult.SearchManager()
        self._init_properties()
        self._init_widgets()
        self._init_signal_handlers()
        self._init_plugins()
        self.load_css()
        self.debug("Initialization complete")

    def _init_plugins(self):
        for name in catapult.conf.plugins:
            try:
                self.debug(f"Initializing plugin {name}")
                self._plugins.append(catapult.util.load_plugin(name))
            except Exception:
                logging.exception(f"Failed to initialize {name}")

    def _init_properties(self):
        # XXX: Not needed anymore? (GTK 4.10.4)
        # We seem to need 'csd' and/or 'ssd' here, otherwise we get
        # graphical glitches with the transparent window background.
        # https://docs.gtk.org/gtk4/class.Window.html#css-nodes
        # self.add_css_class("csd")
        # self.add_css_class("ssd")
        self.add_css_class("catapult-window")
        self.set_icon_name("io.otsaloma.catapult")
        Gtk.Window.set_default_icon_name("io.otsaloma.catapult")
        self.set_decorated(False)
        self.set_default_size(600, -1)
        self.set_resizable(False)

    def _init_signal_handlers(self):
        self.connect("notify::has-toplevel-focus", self._on_notify_has_toplevel_focus)
        self._input_entry.connect("notify::text", self._on_input_entry_notify_text)
        self._icon_theme_handler_id = self._icon_theme.connect("changed", self._on_icon_theme_changed)
        controller = Gtk.EventControllerKey()
        controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.add_controller(controller)
        controller.connect("key-pressed", self._on_key_pressed)

    def _init_widgets(self):
        screen_width, screen_height = catapult.util.get_screen_size()
        input_icon = Gtk.Image()
        input_icon.set_pixel_size(ICON_SIZE_PX/2)
        input_icon.set_from_icon_name(util.lookup_icon(
            "system-search-symbolic",
            "edit-find-symbolic",
            "system-search",
            "edit-find",
        ) or "")
        input_icon.set_icon_size(Gtk.IconSize.LARGE)
        input_icon.add_css_class("catapult-input-icon")
        self._input_entry.add_css_class("catapult-input-entry")
        self._input_entry.set_hexpand(True)
        input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        input_box.add_css_class("catapult-input-box")
        input_box.set_hexpand(True)
        input_box.append(input_icon)
        input_box.append(self._input_entry)
        self._body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._body.add_css_class("catapult-body")
        # Catch mouse press events anywhere on the edges of the window.
        gesture = Gtk.GestureClick()
        self._body.add_controller(gesture)
        gesture.connect("pressed", self._on_gesture_pressed)
        self._body.append(input_box)
        self._result_scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self._result_scroller.set_max_content_height(int(0.5 * screen_height))
        self._result_scroller.set_propagate_natural_height(True)
        self._result_scroller.set_hexpand(True)
        self._result_list.set_can_focus(False)
        self._result_list.add_css_class("catapult-search-result-list")
        for i in range(catapult.conf.max_results):
            row = SearchResultRow()
            row.set_can_focus(False)
            self._result_list.append(row)
            self._result_rows.append(row)
        self._result_scroller.set_child(self._result_list)
        self._body.append(self._result_scroller)
        self._result_scroller.hide()
        self.set_child(self._body)

    def activate_plugin(self, name):
        if name in [x.name for x in self._plugins]: return
        try:
            self.debug(f"Activating plugin {name}")
            self._plugins.append(catapult.util.load_plugin(name))
        except Exception:
            logging.exception("Failed to activate {name}")

    def deactivate_plugin(self, name):
        self.debug(f"Deactivating plugin {name}")
        for i in reversed(range(len(self._plugins))):
            if self._plugins[i].name == name:
                del self._plugins[i]
        # Always write configuration, so that e.g. if changing
        # preferences in the preferences dialog for an inactive
        # plugin, those changes will get saved too.
        plugin = catapult.util.load_plugin_class(name)
        if plugin.conf is not None:
            plugin.conf.write()

    def delete_selected(self):
        row = self._result_list.get_selected_row()
        if row is None: return
        if row.result is None: return
        if row.result.plugin.delete(self, row.result.id):
            self.debug("Delete successful, removing row...")
            self._result_list.unselect_all()
            index = row.get_index()
            row.result = None
            row.set_visible(False)
            self._result_list.remove(row)
            self._result_list.append(row)
            self._result_rows.remove(row)
            self._result_rows.append(row)
            if row_count := self.get_row_count():
                index = min(row_count - 1, index)
                row = self._result_rows[index]
                self._result_list.select_row(row)

    def get_query(self):
        return self._input_entry.get_text()

    def get_row_count(self):
        return sum(x.result is not None for x in self._result_rows)

    def hide(self):
        self._search_manager.history.write_maybe()
        for plugin in self._plugins:
            try:
                plugin.on_window_hide()
            except Exception:
                logging.exception(f"on_window_hide failed for {plugin.name}")
        self._result_list.unselect_all()
        super().hide()

    def launch_selected(self):
        row = self._result_list.get_selected_row()
        if row is None: return
        if row.result is None: return
        self._search_manager.launch(self, row.query, row.result)
        self.hide()

    def load_css(self):
        style = self.get_style_context()
        priority = Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        if self._css_provider is not None:
            style.remove_provider(self._css_provider)
        css = "\n".join((
            catapult.util.load_theme(catapult.conf.theme),
            (catapult.DATA_DIR / "catapult.css").read_text("utf-8"),
        ))
        self._css_provider = Gtk.CssProvider()
        try:
            # The call signature of 'load_from_data' seems to have changed
            # in some GTK version. Also, the whole function is deprecated
            # and since GTK 4.12 we should use 'load_from_string'.
            self._css_provider.load_from_data(css, -1)
        except Exception:
            self._css_provider.load_from_data(bytes(css.encode()))
        display = Gdk.Display.get_default()
        style.add_provider_for_display(display, self._css_provider, priority)

    def _on_gesture_pressed(self, *args, **kwargs):
        self._input_entry.set_text(":")
        self._input_entry.set_position(-1)

    def _on_icon_theme_changed(self, icon_theme):
        self.debug("Icon theme changed")
        self._icon_theme.disconnect(self._icon_theme_handler_id)
        self._icon_theme = icon_theme
        self._icon_theme_handler_id = self._icon_theme.connect("changed", self._on_icon_theme_changed)
        catapult.util.lookup_icon.cache_clear()

    def _on_input_entry_notify_text(self, *args, **kwargs):
        GLib.idle_add(self._on_input_entry_notify_text_do)

    def _on_input_entry_notify_text_do(self, *args, **kwargs):
        query = self.get_query()
        if query == self._prev_query: return
        self._prev_query = query
        results = self._search_manager.search(self._plugins, query)
        for result, row in itertools.zip_longest(results, self._result_rows):
            row.query = query
            row.result = result
            row.set_visible(result is not None)
            if result is None: continue
            row.set_icon(result.icon or "")
            row.title_label.set_text(result.title or "")
            row.description_label.set_text(result.description or "")
            self._set_result_list_height(row)
        self._result_list.select_row(self._result_rows[0])
        self._result_scroller.get_vadjustment().set_value(0)
        self._result_scroller.set_visible(bool(results))

    def _on_key_pressed(self, event_controller_key, keyval, keycode, state, user_data=None):
        if keyval == Gdk.KEY_Up:
            self.select_previous_result()
            return True
        if keyval == Gdk.KEY_Down:
            self.select_next_result()
            return True
        if keyval in [Gdk.KEY_Return, Gdk.KEY_KP_Enter]:
            self.launch_selected()
            return True
        if keyval == Gdk.KEY_Delete:
            # Allow delete to be used both for editing the input query
            # and deleting result items, depending on where the cursor is.
            if self._input_entry.get_position() == len(self._input_entry.get_text()):
                self.delete_selected()
                return True
        if keyval == Gdk.KEY_F1:
            self._input_entry.set_text(":")
            self._input_entry.set_position(-1)
            return True
        if keyval == Gdk.KEY_Escape:
            self.hide()
            return True

    def _on_notify_has_toplevel_focus(self, *args, **kwargs):
        if not self.has_toplevel_focus():
            self.hide()

    def open_about_dialog(self):
        self.hide()
        dialog = catapult.AboutDialog(self)
        dialog.show()

    def open_preferences_dialog(self):
        def on_close_request(dialog, *args, **kwargs):
            dialog.load(self)
            self.write_configuration()
            self.update()
        self.hide()
        dialog = catapult.PreferencesDialog(self)
        dialog.connect("close-request", on_close_request)
        dialog.show()

    def quit(self):
        self._search_manager.history.write()
        self.write_configuration()
        self.destroy()

    def reload_plugins(self):
        for name in catapult.conf.plugins:
            try:
                self.debug(f"Reloading plugin {name}")
                self.deactivate_plugin(name)
                catapult.util.load_plugin_module.cache_clear()
                self.activate_plugin(name)
            except Exception:
                logging.exception(f"Failed to reload {name}")

    def reset_list_height(self):
        self._result_list_height_set = False

    def _scroll_to_row(self, row):
        if not row.is_visible(): return
        x, y = row.translate_coordinates(self._result_list, 0, 0)
        row_height = row.get_preferred_size()[1].height
        list_height = self._result_scroller.get_preferred_size()[1].height
        adjustment = self._result_scroller.get_vadjustment()
        lower = adjustment.get_value()
        upper = lower + list_height
        if y < lower:
            # Scroll up
            adjustment.set_value(y)
        if y > (upper - row_height):
            # Scroll down
            diff = y - (upper - row_height)
            adjustment.set_value(lower + diff)

    def select_next_result(self):
        if not self._result_scroller.is_visible(): return
        row = self._result_list.get_selected_row()
        index = row.get_index() if row else -1
        row_count = self.get_row_count()
        index = min(row_count - 1, index + 1)
        row = self._result_rows[index]
        if not row.is_visible(): return
        self._result_list.select_row(row)
        self._scroll_to_row(row)

    def select_previous_result(self):
        if not self._result_scroller.is_visible(): return
        row = self._result_list.get_selected_row()
        index = row.get_index() if row else 1
        index = max(0, index - 1)
        row = self._result_rows[index]
        if not row.is_visible(): return
        self._result_list.select_row(row)
        self._scroll_to_row(row)

    def set_plugin_active(self, name, active):
        if active:
            return self.activate_plugin(name)
        self.deactivate_plugin(name)

    def _set_result_list_height(self, row):
        if self._result_list_height_set: return
        row_height = row.get_preferred_size()[1].height
        if not row_height: return
        screen_height = catapult.util.get_screen_size()[1]
        row_count = (0.5 * screen_height) // row_height
        row_count = min(row_count, catapult.conf.max_results_visible)
        total_height = row_count * row_height
        self.debug(f"Setting result list height to {row_count} items, {total_height} pixels")
        self._result_scroller.set_max_content_height(total_height)
        self._result_list_height_set = True

    def show(self):
        for plugin in self._plugins:
            try:
                plugin.on_window_show()
            except Exception:
                logging.exception(f"on_window_show failed for {plugin.name}")
        self.set_sensitive(True)
        self.present()
        self._result_list.unselect_all()
        self._result_scroller.hide()
        self._prev_query = ""
        self._input_entry.set_text("")
        self._input_entry.grab_focus()
        super().show()

    def toggle(self, *args, **kwargs):
        self.hide() if self.is_visible() else self.show()

    def update(self):
        for plugin in self._plugins:
            plugin.update_async()

    def write_configuration(self):
        catapult.conf.write()
        for plugin in self._plugins:
            if plugin.conf is not None:
                plugin.conf.write()
