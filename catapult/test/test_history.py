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

import catapult.test
import os
import tempfile

from pathlib import Path


class TestHistory(catapult.test.TestCase):

    def setup_method(self, method):
        self.history = catapult.History()
        handle, self.temp_path = tempfile.mkstemp(prefix="catapult-", suffix=".json")
        self.history.path = Path(self.temp_path)
        self.result = catapult.SearchResult(
            description="Testing",
            fuzzy=False,
            icon="test",
            id="test",
            offset=0,
            plugin=catapult.util.load_plugin("apps"),
            score=1,
            title="Test",
        )

    def teardown_method(self, method):
        os.remove(self.temp_path)

    def test_add_contains(self):
        self.history.add("test", self.result)
        assert self.history.contains("test", self.result)

    def test_count(self):
        self.history.add("test", self.result)
        assert self.history.count == 1
        self.history.add("test", self.result)
        assert self.history.count == 1
        self.history.add("rest", self.result)
        assert self.history.count == 2
        self.history.add("rest", self.result)
        assert self.history.count == 2

    def test_get_score_factor(self):
        factor = self.history.get_score_factor
        assert factor("test", self.result) == 1
        self.history.add("test", self.result)
        assert factor("test", self.result) > 1
        self.history.add("test", self.result)
        assert factor("test", self.result) > 2

    def test_items(self):
        self.history.add("test", self.result)
        assert list(self.history.items())

    def test_prune(self):
        self.history.add("test", self.result)
        assert self.history.count == 1
        self.history.prune()
        assert self.history.count == 1

    def test_read_write(self):
        self.history.add("test", self.result)
        self.history.write()
        self.history.add("rest", self.result)
        self.history.read()
        assert self.history.contains("test", self.result)
        assert not self.history.contains("rest", self.result)
