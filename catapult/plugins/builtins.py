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

from catapult.i18n import _


class BuiltinsPlugin(catapult.Plugin):

    def launch(self, window, id):
        self.debug(f"Launching {id}")
        if id == ":about":
            return window.open_about_dialog()
        if id == ":quit":
            return window.quit()
        if id == ":update":
            return window.update()

    def search(self, query):
        query = query.lower().strip()
        if not query.startswith(":"): return
        icon = catapult.util.lookup_icon(
            "io.otsaloma.catapult",
            "application-x-executable",
        )
        if ":about".startswith(query):
            self.debug(f"Found :about for {query!r}")
            yield catapult.SearchResult(
                description=_("About Catapult"),
                fuzzy=False,
                icon=icon,
                id=":about",
                offset=0,
                plugin=self,
                score=1,
                title=":about",
            )
        if ":quit".startswith(query):
            self.debug(f"Found :quit for {query!r}")
            yield catapult.SearchResult(
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
            yield catapult.SearchResult(
                description=_("Update search index"),
                fuzzy=False,
                icon=icon,
                id=":update",
                offset=0,
                plugin=self,
                score=1,
                title=":update",
            )
