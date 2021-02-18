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

from dataclasses import dataclass


@dataclass
class SearchResult:

    description: str
    fuzzy: bool
    icon: object
    id: str
    offset: int
    plugin: catapult.Plugin
    score: float
    title: str

    def launch(self):
        self.plugin.launch(self.id)


class SearchManager(catapult.DebugMixin):

    def _adjust_score(self, result):
        if result.fuzzy:
            result.score *= 0.5
        if result.offset > 0:
            result.score *= 0.5
        if result.plugin == "apps":
            result.score *= 1.1

    def _get_results(self, plugins, query):
        for name, plugin in plugins.items():
            self.tick()
            results = plugin.search(query)
            elapsed = self.tock()
            yield from results
            self.debug(f"{name} plugin delivered in {elapsed:.0f} ms")

    def search(self, plugins, query):
        if not query: return []
        self.debug(f"Starting search for {query!r}")
        results = list(self._get_results(plugins, query))
        self.debug(f"Found {len(results)} results")
        for result in results:
            self._adjust_score(result)
        results.sort(key=lambda x: (-x.score, x.title, x.description))
        for i, result in enumerate(results[:10]):
            self.debug(f"{i+1}. {result.plugin.name}: {result.title} {result.score:.3f}")
        return results[:catapult.conf.max_results]
