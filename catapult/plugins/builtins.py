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


class BuiltinsPlugin(Plugin):

    title = "Builtins"

    def launch(self, window, id):
        self.debug(f"Launching {id}")
        if id == ":about":
            return window.open_about_dialog()
        if id == ":preferences":
            return window.open_preferences_dialog()
        if id == ":reload-plugins":
            return window.reload_plugins()
        if id == ":reload-theme":
            return window.load_css()
        if id == ":quit":
            return window.quit()
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
        if ":about".startswith(query):
            self.debug(f"Found :about for {query!r}")
            yield SearchResult(
                description=_("About Catapult"),
                fuzzy=False,
                icon=icon,
                id=":about",
                offset=0,
                plugin=self,
                score=1,
                title=":about",
            )
        if ":preferences".startswith(query):
            self.debug(f"Found :preferences for {query!r}")
            yield SearchResult(
                description=_("Catapult preferences"),
                fuzzy=False,
                icon=icon,
                id=":preferences",
                offset=0,
                plugin=self,
                score=1,
                title=":preferences",
            )
        if ":reload-plugins".startswith(query):
            self.debug(f"Found :reload-plugins for {query!r}")
            yield SearchResult(
                description=_("Reload plugins"),
                fuzzy=False,
                icon=icon,
                id=":reload-plugins",
                offset=0,
                plugin=self,
                score=1,
                title=":reload-plugins",
            )
        if ":reload-theme".startswith(query):
            self.debug(f"Found :reload-theme for {query!r}")
            yield SearchResult(
                description=_("Reload theme"),
                fuzzy=False,
                icon=icon,
                id=":reload-theme",
                offset=0,
                plugin=self,
                score=1,
                title=":reload-theme",
            )
        if ":quit".startswith(query):
            self.debug(f"Found :quit for {query!r}")
            yield SearchResult(
                description=_("Quit Catapult"),
                fuzzy=False,
                icon=icon,
                id=":quit",
                offset=0,
                plugin=self,
                score=1,
                title=":quit",
            )
        if ":update".startswith(query):
            self.debug(f"Found :update for {query!r}")
            yield SearchResult(
                description=_("Update search index"),
                fuzzy=False,
                icon=icon,
                id=":update",
                offset=0,
                plugin=self,
                score=1,
                title=":update",
            )
