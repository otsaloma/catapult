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

class TestCharactersPlugin(catapult.test.TestCase):

    def setup_method(self, method):
        self.plugin = catapult.plugins.characters.CharactersPlugin()

    def test___init__(self):
        assert self.plugin._characters

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

    def test_search_emoji_terms(self):
        assert list(self.plugin.search("<"))
        assert list(self.plugin.search("<3"))
