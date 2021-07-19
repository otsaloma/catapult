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
import tempfile

from pathlib import Path


class TestUtil(catapult.test.TestCase):

    def test_atomic_write(self):
        path = Path(tempfile.mkstemp()[1])
        catapult.util.atomic_write(path, "Hello", "utf-8")
        assert path.exists()
        assert path.read_text("utf-8") == "Hello"
        path.unlink()

    def test_find_plugin(self):
        module = catapult.util.find_plugin("apps")
        assert inspect.ismodule(module)

    def test_find_theme(self):
        path = catapult.util.find_theme("dark")
        assert path.exists()

    def test_get_desktop_environment(self):
        catapult.util.get_desktop_environment()

    def test_get_monitor(self):
        assert catapult.util.get_monitor()

    def test_get_screen_size(self):
        width, height = catapult.util.get_screen_size()
        assert width and height

    def test_is_path(self):
        assert catapult.util.is_path("/home/osmo/.bashrc")
        assert not catapult.util.is_path("file:///home/osmo/.bashrc")

    def test_is_plugin_class(self):
        assert catapult.util.is_plugin_class(catapult.plugins.apps.AppsPlugin)

    def test_is_uri(self):
        assert catapult.util.is_uri("file:///home/osmo/.bashrc")
        assert not catapult.util.is_uri("/home/osmo/.bashrc")

    def test_list_custom_plugins(self):
        catapult.util.list_custom_plugins()

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

    def test_load_plugin_class(self):
        cls = catapult.util.load_plugin_class("apps")
        assert catapult.util.is_plugin_class(cls)

    def test_load_plugin_module(self):
        module = catapult.util.load_plugin_module("apps")
        assert inspect.ismodule(module)

    def test_load_theme(self):
        assert catapult.util.load_theme("dark")

    def test_lookup_icon(self):
        catapult.util.lookup_icon("folder")
        catapult.util.lookup_icon("xxx")
