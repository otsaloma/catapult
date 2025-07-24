# -*- coding: utf-8 -*-

# Copyright (C) 2025 Osmo Salomaa
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
import time

class TestCharactersPlugin(catapult.test.TestCase):

    def setup_method(self, method):
        self.plugin = catapult.plugins.characters.CharactersPlugin()
        for i in range(100):
            if not self.plugin.data_loaded:
                time.sleep(0.1)

    def test___init__(self):
        nemoji = sum(x.is_emoji for x in self.plugin._characters)
        nother = len(self.plugin._characters) - nemoji
        assert nemoji > 0
        assert nother > 0

    def test_search(self):
        assert list(self.plugin.search("e"))
        assert list(self.plugin.search("ep"))
        assert list(self.plugin.search("eps"))
        assert list(self.plugin.search("epsi"))
        assert list(self.plugin.search("epsil"))
        assert list(self.plugin.search("epsilo"))
        assert list(self.plugin.search("epsilon"))

    def test_search_emoji(self):
        assert list(self.plugin.search("g"))
        assert list(self.plugin.search("gr"))
        assert list(self.plugin.search("gri"))
        assert list(self.plugin.search("grin"))

    def test_search_emoji_flag(self):
        assert list(self.plugin.search("andorra"))

    def test_search_emoji_multi(self):
        assert list(self.plugin.search("face with spiral eyes"))

    def test_search_emoji_terms(self):
        assert list(self.plugin.search("<3"))
