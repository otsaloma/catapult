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
import json
import math
import time


class History(catapult.DebugMixin):

    path = catapult.CONFIG_HOME / "history.json"

    def __init__(self):
        self._items = {}
        self._time_saved = -1

    def add(self, query, result):
        self.debug(f"Adding {query!r} → {result.plugin.name}: {result.id}")
        item = self._items
        item = item.setdefault(query, {})
        item = item.setdefault(result.plugin.name, {})
        item = item.setdefault(result.id, [])
        item.append(int(time.time()))

    def contains(self, query, result):
        return bool(self._items
                    .get(query, {})
                    .get(result.plugin.name, {})
                    .get(result.id, []))

    @property
    def count(self):
        return sum(1 for x in self.items())

    def get_score_factor(self, query, result):
        item = self._items
        item = item.get(query, {})
        item = item.get(result.plugin.name, {})
        item = item.get(result.id, [])
        # days = seq(0, 30, 1); qplot(days, exp(-0.15 * days), geom="line")
        return 1 + sum(math.exp(-0.15 * (time.time() - x) / 86400) for x in item)

    def items(self):
        for query in self._items:
            for plugin in self._items[query]:
                for id in self._items[query][plugin]:
                    yield (query,
                           plugin,
                           id,
                           self._items[query][plugin][id])

    def prune(self):
        threshold = time.time() - 30 * 86400
        for query in list(self._items):
            for plugin in list(self._items[query]):
                for id in list(self._items[query][plugin]):
                    times = self._items[query][plugin][id]
                    times = sorted(x for x in times if x > threshold)[-5:]
                    self._items[query][plugin][id] = times
        # Remove resulting empty branches.
        for query in list(self._items):
            for plugin in list(self._items[query]):
                for id in list(self._items[query][plugin]):
                    if not self._items[query][plugin][id]:
                        del self._items[query][plugin][id]
                if not self._items[query][plugin]:
                    del self._items[query][plugin]
            if not self._items[query]:
                del self._items[query]

    def read(self):
        if not self.path.exists(): return
        text = self.path.read_text("utf-8")
        self._items = json.loads(text)
        self.debug(f"Read {self.count} items")
        self._time_saved = time.time()

    def write(self):
        self.prune()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        blob = json.dumps(self._items, ensure_ascii=False, indent=2, sort_keys=True)
        try:
            catapult.util.atomic_write(self.path, blob + "\n", "utf-8")
        except OSError as error:
            return print(f"Writing {str(self.path)} failed: {str(error)}")
        self.debug(f"Wrote {self.count} items")
        self._time_saved = time.time()

    def write_maybe(self):
        # Allow writing history at semi-regular intervals.
        elapsed = time.time() - self._time_saved
        if elapsed < 3600: return
        self.write()
