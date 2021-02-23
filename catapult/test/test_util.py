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
import inspect


class TestUtil(catapult.test.TestCase):

    def test_find_plugin(self):
        module = catapult.util.find_plugin("apps")
        assert inspect.ismodule(module)

    def test_find_theme(self):
        path = catapult.util.find_theme("dark")
        assert path.exists()

    def test_get_desktop_environment(self):
        catapult.util.get_desktop_environment()

    def test_get_screen_size(self):
        width, height = catapult.util.get_screen_size()
        assert width and height

    def test_is_path(self):
        assert catapult.util.is_path("/home/osmo/.bashrc")
        assert not catapult.util.is_path("file:///home/osmo/.bashrc")

    def test_is_uri(self):
        assert catapult.util.is_uri("file:///home/osmo/.bashrc")
        assert not catapult.util.is_uri("/home/osmo/.bashrc")

    def test_list_plugins(self):
        plugins = list(catapult.util.list_plugins())
        assert "apps" in [x[0] for x in plugins]
        for name, module in plugins:
            assert inspect.ismodule(module) or module.exists()

    def test_list_themes(self):
        themes = list(catapult.util.list_themes())
        assert "dark" in [x[0] for x in themes]
        for name, path in themes:
            assert path.exists()

    def test_load_plugin(self):
        plugin = catapult.util.load_plugin("apps")
        assert isinstance(plugin, catapult.Plugin)

    def test_load_theme(self):
        assert catapult.util.load_theme("dark")

    def test_lookup_icon(self):
        catapult.util.lookup_icon("folder")
        catapult.util.lookup_icon("xxx")
