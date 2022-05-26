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
import traceback

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

    def launch(self, window):
        try:
            self.plugin.launch(window, self.id)
        except Exception:
            traceback.print_exc()
            print(f"Failed to launch {self.plugin.name} result {self.id}")


class SearchManager(catapult.DebugMixin):

    def __init__(self):
        self.history = catapult.History()
        self.history.read()

    def _adjust_score(self, query, result):
        if result.fuzzy:
            result.score *= 0.5
        if result.offset > 0:
            result.score *= 0.5
        if result.plugin.save_history:
            result.score *= self.history.get_score_factor(query, result)

    def _get_results(self, plugins, query):
        for plugin in plugins:
            self.tick()
            try:
                yield from plugin.search(query)
                elapsed = self.tock()
                self.debug(f"{plugin.name} delivered in {elapsed:.0f} ms")
            except Exception:
                traceback.print_exc()
                print(f"Failed to get search results from {plugin.name}")

    def launch(self, window, query, result):
        if result.plugin.save_history:
            self.history.add(query, result)
        result.launch(window)

    def search(self, plugins, query):
        if not query: return []
        self.debug(f"Starting search for {query!r}")
        if query.strip().startswith(":"):
            plugins = [x for x in plugins if x.name == "builtins"]
        results = list(self._get_results(plugins, query))
        self.debug(f"Found {len(results)} results")
        self.tick()
        for result in results:
            self._adjust_score(query, result)
        results.sort(key=lambda x: (-x.score, x.title, x.description))
        elapsed = self.tock()
        self.debug(f"Adjusted scores in {elapsed:.0f} ms")
        for i, result in enumerate(results[:catapult.conf.max_results_visible]):
            self.debug(f"{i+1}. {result.plugin.name}: {result.title} {result.score:.3f}")
        return results[:catapult.conf.max_results]
