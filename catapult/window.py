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
import logging

from catapult import util
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Keybinder
from gi.repository import Pango

ICON_SIZE = Gtk.IconSize.DIALOG
ICON_SIZE_PX = 48
XOFFSET = 0.50
YOFFSET = 0.25


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
        self.description_label = Gtk.Label()
        self.description_label.set_xalign(0)
        self.description_label.set_yalign(0)
        self.description_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.get_style_context().add_class("catapult-search-result")
        self.icon.get_style_context().add_class("catapult-search-result-icon")
        self.title_label.get_style_context().add_class("catapult-search-result-title")
        self.description_label.get_style_context().add_class("catapult-search-result-description")
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        hbox.pack_start(self.icon, expand=False, fill=False, padding=0)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        vbox.pack_start(self.title_label, expand=True, fill=True, padding=0)
        vbox.pack_start(self.description_label, expand=True, fill=True, padding=0)
        hbox.pack_start(vbox, expand=True, fill=True, padding=0)
        self.add(hbox)

    def set_icon(self, icon):
        (self.icon.set_from_gicon if isinstance(icon, Gio.Icon)
         else self.icon.set_from_icon_name)(icon, ICON_SIZE)


class Window(Gtk.ApplicationWindow, catapult.DebugMixin, catapult.WindowMixin):

    def __init__(self):
        GObject.GObject.__init__(self)
        self._body = None
        self._css_provider = None
        self._icon_theme = Gtk.IconTheme.get_default()
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
        self._toggle_key = None
        self._init_properties()
        self._init_visual()
        self._init_widgets()
        self._init_signal_handlers()
        self._init_keys()
        self._init_plugins()
        self.load_css()
        self.set_position_offset(XOFFSET, YOFFSET)
        self.debug("Initialization complete")

    def _init_keys(self):
        Keybinder.init()
        def bind_toggle_key(self, key):
            self.bind_toggle_key(key)
            return False # to not be called again.
        GLib.idle_add(bind_toggle_key, self, catapult.conf.toggle_key)

    def _init_plugins(self):
        for name in catapult.conf.plugins:
            try:
                self.debug(f"Initializing plugin {name}")
                self._plugins.append(catapult.util.load_plugin(name))
            except Exception:
                logging.exception(f"Failed to initialize {name}")

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
        self.connect("key-press-event", self._on_key_press_event)
        self.connect("notify::has-toplevel-focus", self._on_notify_has_toplevel_focus)
        self._input_entry.connect("notify::text", self._on_input_entry_notify_text)
        self._icon_theme_handler_id = self._icon_theme.connect("changed", self._on_icon_theme_changed)

    def _init_visual(self):
        # Make window transparent to allow rounded corners.
        screen = Gdk.Screen.get_default()
        visual = screen.get_rgba_visual()
        if not visual: return
        self.set_app_paintable(True)
        self.set_visual(visual)

    def _init_widgets(self):
        screen_width, screen_height = catapult.util.get_screen_size()
        input_icon = Gtk.Image()
        input_icon.set_pixel_size(ICON_SIZE_PX/2)
        input_icon.set_from_icon_name(util.lookup_icon(
            "system-search-symbolic",
            "edit-find-symbolic",
            "system-search",
            "edit-find",
        ) or "", ICON_SIZE)
        input_icon.get_style_context().add_class("catapult-input-icon")
        self._input_entry.get_style_context().add_class("catapult-input-entry")
        input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        input_box.get_style_context().add_class("catapult-input-box")
        input_box.pack_start(input_icon, expand=False, fill=False, padding=0)
        input_box.pack_start(self._input_entry, expand=True, fill=True, padding=0)
        self._body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._body.get_style_context().add_class("catapult-body")
        self._body.pack_start(input_box, expand=True, fill=True, padding=0)
        self._result_scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self._result_scroller.set_max_content_height(int(0.5 * screen_height))
        self._result_scroller.set_propagate_natural_height(True)
        self._result_list.set_can_focus(False)
        self._result_list.get_style_context().add_class("catapult-search-result-list")
        for i in range(catapult.conf.max_results):
            row = SearchResultRow()
            row.set_can_focus(False)
            self._result_list.add(row)
            self._result_rows.append(row)
        self._result_scroller.add(self._result_list)
        self._body.pack_start(self._result_scroller, expand=True, fill=True, padding=0)
        self._result_scroller.hide()
        event_box = Gtk.EventBox()
        # Catch mouse press events anywhere on the edges of the window.
        event_box.connect("button-press-event", self._on_button_press_event)
        event_box.add(self._body)
        event_box.show_all()
        self.add(event_box)

    def activate_plugin(self, name):
        if name in [x.name for x in self._plugins]: return
        try:
            self.debug(f"Activating plugin {name}")
            self._plugins.append(catapult.util.load_plugin(name))
        except Exception:
            logging.exception("Failed to activate {name}")

    def bind_toggle_key(self, key):
        self.unbind_toggle_key()
        self.debug(f"Binding toggle key {key}")
        success = Keybinder.bind(key, self.toggle)
        if success:
            self._toggle_key = key
            return success
        else:
            self.debug(f"Failed to bind toggle key {key}")
            return success

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
            self._result_list.add(row)
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
        catapult.util.iterate_main()
        super().hide()

    def launch_selected(self):
        row = self._result_list.get_selected_row()
        if row is None: return
        if row.result is None: return
        self._search_manager.launch(self, row.query, row.result)
        self.hide()

    def load_css(self):
        style = self.get_style_context()
        screen = Gdk.Screen.get_default()
        priority = Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        if self._css_provider is not None:
            style.remove_provider_for_screen(screen, self._css_provider)
        css = "\n".join((
            catapult.util.load_theme(catapult.conf.theme),
            (catapult.DATA_DIR / "catapult.css").read_text("utf-8"),
        ))
        self._css_provider = Gtk.CssProvider()
        self._css_provider.load_from_data(bytes(css.encode()))
        style.add_provider_for_screen(screen, self._css_provider, priority)

    def _on_button_press_event(self, *args, **kwargs):
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

    def _on_key_press_event(self, window, event):
        if event.keyval == Gdk.KEY_Up:
            self.select_previous_result()
            return True
        if event.keyval == Gdk.KEY_Down:
            self.select_next_result()
            return True
        if event.keyval in [Gdk.KEY_Return, Gdk.KEY_KP_Enter]:
            self.launch_selected()
            return True
        if event.keyval == Gdk.KEY_Delete:
            # Allow delete to be used both for editing the input query
            # and deleting result items, depending on where the cursor is.
            if self._input_entry.get_position() == len(self._input_entry.get_text()):
                self.delete_selected()
                return True
        if event.keyval == Gdk.KEY_F1:
            self._input_entry.set_text(":")
            self._input_entry.set_position(-1)
            return True
        if event.keyval == Gdk.KEY_Escape:
            self.hide()
            return True

    def _on_notify_has_toplevel_focus(self, *args, **kwargs):
        if not self.has_toplevel_focus():
            self.hide()

    def open_about_dialog(self):
        def on_response(dialog, response):
            dialog.destroy()
        self.hide()
        dialog = catapult.AboutDialog(self)
        dialog.connect("response", on_response)
        dialog.run()

    def open_preferences_dialog(self):
        def on_response(dialog, response):
            dialog.load(self)
            self.write_configuration()
            self.update()
            dialog.destroy()
        self.hide()
        dialog = catapult.PreferencesDialog(self)
        dialog.connect("response", on_response)
        dialog.run()

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

    def select_next_result(self):
        if not self._result_scroller.is_visible(): return
        row = self._result_list.get_selected_row()
        index = row.get_index() if row else -1
        row_count = self.get_row_count()
        index = min(row_count - 1, index + 1)
        row = self._result_rows[index]
        if not row.is_visible(): return
        self._result_list.select_row(row)
        row.grab_focus()
        self._input_entry.grab_focus()
        self._input_entry.set_position(-1)

    def select_previous_result(self):
        if not self._result_scroller.is_visible(): return
        row = self._result_list.get_selected_row()
        index = row.get_index() if row else 1
        index = max(0, index - 1)
        row = self._result_rows[index]
        if not row.is_visible(): return
        self._result_list.select_row(row)
        row.grab_focus()
        self._input_entry.grab_focus()
        self._input_entry.set_position(-1)

    def set_plugin_active(self, name, active):
        if active:
            return self.activate_plugin(name)
        self.deactivate_plugin(name)

    def _set_result_list_height(self, row):
        if self._result_list_height_set: return
        row_height = row.get_preferred_height()[1]
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
        self._update_position()
        self.move(*self._position)
        timestamp = Keybinder.get_current_event_time()
        self.present_with_time(timestamp)
        self._result_list.unselect_all()
        self._result_scroller.hide()
        self._prev_query = ""
        self._input_entry.set_text("")
        self._input_entry.grab_focus()
        super().show()

    def toggle(self, *args, **kwargs):
        self.hide() if self.is_visible() else self.show()

    def unbind_toggle_key(self):
        if not self._toggle_key: return
        self.debug(f"Unbinding toggle key {self._toggle_key}")
        Keybinder.unbind(self._toggle_key)
        self._toggle_key = None

    def update(self):
        for plugin in self._plugins:
            plugin.update_async()

    def _update_position(self):
        if self._monitor.is_primary() != self._monitor_was_primary:
            self.debug("Primary monitor changed, updating position")
            self.set_position_offset(XOFFSET, YOFFSET)

    def write_configuration(self):
        catapult.conf.write()
        for plugin in self._plugins:
            if plugin.conf is not None:
                plugin.conf.write()
