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

class TestSearchManager(catapult.test.TestCase):

    def setup_method(self, method):
        self.plugins = [catapult.util.load_plugin(x) for x in catapult.conf.plugins]
        self.search_manager = catapult.SearchManager()

    def test_search(self):
        self.search_manager.search(self.plugins, "t")
        self.search_manager.search(self.plugins, "te")
        self.search_manager.search(self.plugins, "tes")
        self.search_manager.search(self.plugins, "test")
