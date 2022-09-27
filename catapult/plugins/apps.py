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

import re

from catapult.api import Plugin
from catapult.api import SearchResult
from catapult.i18n import _
from gi.repository import Gio


class AppsPlugin(Plugin):

    title = _("Apps")

    def __init__(self):
        super().__init__()
        self._index = {}
        self.update_async()
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
            id = app.get_id()
            if id == "io.otsaloma.catapult.desktop": continue
            yield id, app

    def on_window_show(self):
        self.update_async()

    def search(self, query):
        query = query.lower().strip()
        results = Gio.DesktopAppInfo.search(query)
        for i, batch in enumerate(results):
            for id in batch:
                if id not in self._index: continue
                app = self._index[id]
                self.debug(f"Found {id} for {query!r}")
                yield SearchResult(
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
        self.debug("Updating index...")
        self._index = dict(self._list_apps())
        self.debug(f"{len(self._index)} items in index")
