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
import re
import time

from catapult.i18n import _
from gi.repository import Gio
from gi.repository import Gtk


class AppsScanInterval(catapult.PreferencesItem):

    def __init__(self, plugin=None):
        super().__init__(plugin=plugin)
        self.label = Gtk.Label(label=_("Scan interval"))
        self.spin = Gtk.SpinButton()
        self.spin.set_increments(1, 5)
        self.spin.set_range(1, 1440)
        self.unit = Gtk.Label(label=_("minutes"))
        self.widget = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.widget.pack_start(self.spin, expand=False, fill=False, padding=0)
        self.widget.pack_start(self.unit, expand=False, fill=False, padding=0)

    def dump(self, window):
        value = self.plugin.conf.scan_interval
        self.spin.set_value(int(round(value / 60)))

    def load(self, window):
        value = self.spin.get_value_as_int()
        self.plugin.conf.scan_interval = value * 60


class AppsPlugin(catapult.Plugin):

    conf_defaults = {
        "scan_interval": 900, # s
    }
    preferences_items = [AppsScanInterval]
    title = _("Apps")

    def __init__(self):
        super().__init__()
        self._index = {}
        self._time_updated = -1
        self.update_async()
        monitor = Gio.AppInfoMonitor.get()
        monitor.connect("changed", self._on_app_info_monitor_changed)
        self.debug("Initialization complete")

    def _get_description(self, app):
        description = app.get_commandline()
        description = re.sub(r" %\w\b", "", description)
        description = re.sub(r" --$", "", description)
        return description.strip()

    def _get_fuzzy(self, app, query):
        return query not in app.get_name().lower()

    def _get_offset(self, app, query):
        offset = app.get_name().lower().find(query)
        return offset if offset >= 0 else 1000

    def launch(self, window, id):
        if not id in self._index: return
        app = self._index[id]
        self.debug(f"Launching {id}")
        app.launch_uris(uris=None, context=None)

    def _list_apps(self):
        key = lambda x: x.get_filename().lower()
        for app in sorted(Gio.AppInfo.get_all(), key=key):
            if not app.should_show(): continue
            if app.get_id() == "io.otsaloma.catapult.desktop": continue
            self.debug(f"Indexing {app.get_filename()}")
            yield app.get_id(), app

    def _on_app_info_monitor_changed(self, *args, **kwargs):
        self._time_updated = -1

    def on_window_show(self):
        elapsed = time.time() - self._time_updated
        if elapsed < self.conf.scan_interval: return
        self.update_async()

    def search(self, query):
        query = query.lower().strip()
        results = Gio.DesktopAppInfo.search(query)
        for i, batch in enumerate(results):
            for id in batch:
                if id not in self._index: continue
                app = self._index[id]
                self.debug(f"Found {id} for {query!r}")
                yield catapult.SearchResult(
                    description=self._get_description(app),
                    fuzzy=self._get_fuzzy(app, query),
                    icon=app.get_icon() or "application-x-executable",
                    id=app.get_id(),
                    offset=self._get_offset(app, query),
                    plugin=self,
                    score=1.1*0.9**i,
                    title=app.get_name(),
                )

    def update(self):
        self._time_updated = time.time()
        self._index = dict(self._list_apps())
        self.debug(f"{len(self._index)} items in index")
