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

from catapult.api import lookup_icon
from catapult.api import Plugin
from catapult.api import SearchResult
from catapult.i18n import _
from catapult.i18n import __

COMMANDS = {
    ":about":          __("About Catapult"),
    ":preferences":    __("Catapult preferences"),
    ":quit":           __("Quit Catapult"),
    ":reload-plugins": __("Reload plugins"),
    ":reload-theme":   __("Reload theme"),
    ":update":         __("Update search index"),
}

class BuiltinsPlugin(Plugin):

    title = "Builtins"

    def launch(self, window, id):
        self.debug(f"Launching {id}")
        if id == ":about":
            return window.open_about_dialog()
        if id == ":preferences":
            return window.open_preferences_dialog()
        if id == ":quit":
            return window.quit()
        if id == ":reload-plugins":
            return window.reload_plugins()
        if id == ":reload-theme":
            return window.load_css()
        if id == ":update":
            return window.update()

    def search(self, query):
        query = query.lower().strip()
        # List all builtin commands with '?'.
        query = ":" if query == "?" else query
        if not query.startswith(":"): return
        icon = lookup_icon(
            "io.otsaloma.catapult",
            "application-x-executable",
        )
        for id, description in COMMANDS.items():
            if not id.startswith(query): continue
            self.debug(f"Found {id} for {query!r}")
            yield SearchResult(
                description=_(description),
                fuzzy=False,
                icon=icon,
                id=id,
                offset=0,
                plugin=self,
                score=1,
                title=id,
            )
