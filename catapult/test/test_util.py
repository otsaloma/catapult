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


class TestUtil(catapult.test.TestCase):

    def test_find_theme(self):
        path = catapult.util.find_theme("dark")
        assert os.path.isfile(path)

    def test_get_data_path(self):
        path = catapult.util.get_data_path("themes", "dark.css")
        assert os.path.isfile(path)

    def test_list_themes(self):
        themes = list(catapult.util.list_themes())
        assert "dark" in [x[0] for x in themes]
        for theme, path in themes:
            assert os.path.isfile(path)

    def test_read_theme(self):
        css = catapult.util.read_theme("dark")
        assert "@input-font" not in css
