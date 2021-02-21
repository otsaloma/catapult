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
import fnmatch
import glob
import os
import time

from dataclasses import dataclass
from gi.repository import Gio
from pathlib import Path
from threading import Thread


@dataclass
class File:

    icon: Gio.Icon
    location: str
    title: str

    @property
    def uri(self):
        if catapult.util.is_uri(self.location):
            return self.location
        return Path(self.location).as_uri()


class FilesPlugin(catapult.Plugin):

    def __init__(self):
        super().__init__()
        self._index = []
        self._time_updated = -1
        self._update_index_async()
        self.debug("Initialization complete")

    def _get_file_info(self, uri):
        file = Gio.File.new_for_uri(uri)
        return file.query_info("*", Gio.FileQueryInfoFlags.NONE, None)

    def launch(self, id):
        file = Gio.File.new_for_uri(id)
        app = file.query_default_handler()
        self.debug(f"Launching {id}")
        app.launch_uris(uris=[id], context=None)

    def on_window_hide(self):
        self._update_index_async_maybe()

    def on_window_show(self):
        self._update_index_async_maybe()

    def search(self, query):
        for file in self._index:
            offset = file.title.lower().find(query)
            if offset < 0: continue
            self.debug(f"Found {file.location} for {query!r}")
            if file.location == "trash:///":
                # Avoid using an outdated full/empty icon for trash.
                info = self._get_file_info(file.location)
                file.icon = info.get_icon()
            yield catapult.SearchResult(
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
                   for x in catapult.conf.files_exclude)

    def _update_index(self):
        index = []
        for pattern in catapult.conf.files_include:
            pattern = os.path.expanduser(pattern)
            for path in glob.iglob(pattern, recursive=True):
                path = path.rstrip(os.sep)
                if self._should_exclude(path): continue
                self.debug(f"Indexing {path}")
                uri = Path(path).as_uri()
                info = self._get_file_info(uri)
                icon = info.get_icon()
                title = os.path.basename(path)
                index.append(File(icon=icon, location=path, title=title))
        for uri in ["computer:///", "recent:///", "trash:///"]:
            try:
                self.debug(f"Indexing {uri}")
                info = self._get_file_info(uri)
                icon = info.get_icon()
                title = info.get_display_name()
                index.append(File(icon=icon, location=uri, title=title))
            except Exception as error:
                self.debug(f"Failed to index {uri}: {str(error)}")
        self.debug(f"{len(index)} item in index")
        self._index = index
        self._time_updated = time.time()

    def _update_index_async(self):
        Thread(target=self._update_index, daemon=True).start()

    def _update_index_async_maybe(self):
        elapsed = time.time() - self._time_updated
        if elapsed > catapult.conf.files_scan_interval:
            self._update_index_async()
