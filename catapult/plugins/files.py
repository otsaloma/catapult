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

import contextlib
import fnmatch
import glob
import itertools
import os
import time

from catapult.api import is_path
from catapult.api import is_uri
from catapult.api import Plugin
from catapult.api import PreferencesItem
from catapult.api import SearchResult
from catapult.i18n import _
from dataclasses import dataclass
from gi.repository import Gio
from gi.repository import GObject
from gi.repository import Gtk
from pathlib import Path


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
        self.text_view.add_css_class("monospace")
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


class FilesInclude(PreferencesItem):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = Gtk.Label(label=_("Include patterns"))
        self.widget = Gtk.Button()
        self.widget.set_label(_("Edit"))
        self.widget.connect("clicked", self._on_clicked)

    def _on_clicked(self, *args, **kwargs):
        text = "\n".join(self.conf.include)
        parent = self.widget.get_ancestor(Gtk.Window)
        dialog = PatternEditDialog(parent, text)
        dialog.connect("response", self._on_response)
        dialog.run()

    def _on_response(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            patterns = dialog.get_text().strip().splitlines()
            patterns = [x.strip() for x in patterns]
            self.conf.include = patterns
        dialog.destroy()


class FilesExclude(PreferencesItem):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = Gtk.Label(label=_("Exclude patterns"))
        self.widget = Gtk.Button()
        self.widget.set_label(_("Edit"))
        self.widget.connect("clicked", self._on_clicked)

    def _on_clicked(self, *args, **kwargs):
        text = "\n".join(self.conf.exclude)
        parent = self.widget.get_ancestor(Gtk.Window)
        dialog = PatternEditDialog(parent, text)
        dialog.connect("response", self._on_response)
        dialog.run()

    def _on_response(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            patterns = dialog.get_text().strip().splitlines()
            patterns = [x.strip() for x in patterns]
            self.conf.exclude = patterns
        dialog.destroy()


class FilesScanInterval(PreferencesItem):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = Gtk.Label(label=_("Scan interval"))
        self.spin = Gtk.SpinButton()
        self.spin.set_increments(1, 5)
        self.spin.set_range(1, 1440)
        self.unit = Gtk.Label(label=_("minutes"))
        self.widget = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.widget.append(self.spin)
        self.widget.append(self.unit)

    def dump(self, window):
        value = self.conf.scan_interval
        self.spin.set_value(int(round(value / 60)))

    def load(self, window):
        value = self.spin.get_value_as_int()
        self.conf.scan_interval = value * 60


@dataclass
class File:

    icon: Gio.Icon
    location: str
    title: str

    @property
    def uri(self):
        if is_uri(self.location):
            return self.location
        return Path(self.location).as_uri()


class FilesPlugin(Plugin):

    conf_defaults = {
        "exclude": ["lost+found"],
        "include": [os.path.expanduser("~/*")],
        "scan_interval": 900, # s
    }
    preferences_items = [FilesInclude, FilesExclude, FilesScanInterval]
    title = _("Files")

    def __init__(self):
        super().__init__()
        self._index = []
        self._time_updated = -1
        self.update_async()
        self.debug("Initialization complete")

    def _get_file(self, location):
        info = self._get_file_info(location)
        icon = info.get_icon()
        title = info.get_display_name()
        return File(icon=icon, location=location, title=title)

    def _get_file_info(self, location):
        if is_path(location):
            location = Path(location).as_uri()
        file = Gio.File.new_for_uri(location)
        return file.query_info("*", Gio.FileQueryInfoFlags.NONE, None)

    def launch(self, window, id):
        file = Gio.File.new_for_uri(id)
        app = file.query_default_handler()
        self.debug(f"Launching {id}")
        app.launch_uris(uris=[id], context=None)

    def _list_files(self):
        for pattern in self.conf.include:
            pattern = os.path.expanduser(pattern)
            for path in glob.iglob(pattern, recursive=True):
                path = path.rstrip(os.sep)
                if self._should_exclude(path): continue
                self.debug(f"Indexing {path}")
                yield self._get_file(path)

    def _list_special(self):
        for uri in ["computer:///", "recent:///", "trash:///"]:
            with contextlib.suppress(Exception):
                self.debug(f"Indexing {uri}")
                yield self._get_file(uri)

    def on_window_show(self):
        elapsed = time.time() - self._time_updated
        if elapsed < self.conf.scan_interval: return
        self.update_async()

    def search(self, query):
        query = query.lower().strip()
        for file in self._index:
            offset = file.title.lower().find(query)
            if offset < 0 and file.location.endswith(":///"):
                # Check location for special URIs too as the display name
                # seems to sometimes be translated, sometimes not.
                offset = file.location.lower().find(query)
            if offset < 0: continue
            self.debug(f"Found {file.location} for {query!r}")
            if file.location == "trash:///":
                # Avoid using an outdated full/empty icon for trash.
                info = self._get_file_info(file.location)
                file.icon = info.get_icon()
            yield SearchResult(
                description=file.location,
                fuzzy=False,
                icon=file.icon,
                id=file.uri,
                offset=offset,
                plugin=self,
                score=1,
                title=file.title,
            )

    def _should_exclude(self, path):
        return any(os.path.basename(path) == x or fnmatch.fnmatch(path, x)
                   for x in self.conf.exclude)

    def update(self):
        self._time_updated = time.time()
        self._index = list(itertools.chain(self._list_files(), self._list_special()))
        self.debug(f"{len(self._index)} items in index")
