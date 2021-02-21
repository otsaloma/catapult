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

from gi.repository import Gio
from threading import Thread


class AppsPlugin(catapult.Plugin):

    def __init__(self):
        super().__init__()
        self._index = {}
        self._time_updated = -1
        self._update_index_async()
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

    def launch(self, id):
        if not id in self._index: return
        app = self._index[id]
        self.debug(f"Launching {id}")
        app.launch_uris(uris=None, context=None)

    def _on_app_info_monitor_changed(self, *args, **kwargs):
        self._time_updated = -1

    def on_window_hide(self):
        self._update_index_async_maybe()

    def on_window_show(self):
        self._update_index_async_maybe()

    def search(self, query):
        results = Gio.DesktopAppInfo.search(query)
        for i, batch in enumerate(results):
            for id in batch:
                if id not in self._index: continue
                app = self._index[id]
                self.debug(f"Found {id} for {query!r}")
                yield catapult.SearchResult(
                    description=self._get_description(app),
                    fuzzy=self._get_fuzzy(app, query),
                    icon=app.get_icon() or Gio.ThemedIcon.new("application-x-executable"),
                    id=app.get_id(),
                    offset=self._get_offset(app, query),
                    plugin=self,
                    score=0.9**i,
                    title=app.get_name(),
                )

    def _update_index(self):
        index = {}
        sort_key = lambda x: x.get_filename().lower()
        for app in sorted(Gio.AppInfo.get_all(), key=sort_key):
            if not app.should_show(): continue
            self.debug(f"Indexing {app.get_filename()}")
            index[app.get_id()] = app
        self.debug(f"{len(index)} item in index")
        self._index = index
        self._time_updated = time.time()

    def _update_index_async(self):
        Thread(target=self._update_index, daemon=True).start()

    def _update_index_async_maybe(self):
        elapsed = time.time() - self._time_updated
        if elapsed > catapult.conf.apps_scan_interval:
            self._update_index_async()
