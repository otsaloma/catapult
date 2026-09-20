# -*- coding: utf-8 -*-

# Copyright (C) 2026 Osmo Salomaa
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

from gi.repository import GLib
from types import SimpleNamespace
from unittest.mock import Mock

class TestWindowsPlugin(catapult.test.TestCase):

    def setup_method(self, method):
        self.plugin = catapult.plugins.windows.WindowsPlugin()

    def test_delete(self):
        self.plugin._call = Mock()
        assert self.plugin.delete(None, "42")
        self.plugin._call.assert_called_once_with("Close", GLib.Variant("(t)", (42,)), None)
        self.plugin._call.return_value = None
        assert not self.plugin.delete(None, "42")

    def test_on_result_selected(self):
        self.plugin._call = Mock()
        result = SimpleNamespace(plugin=self.plugin, id="42")
        self.plugin.on_result_selected(result)
        self.plugin._call.assert_called_once_with("Preview", GLib.Variant("(t)", (42,)), None)
        self.plugin.on_result_selected(None)
        self.plugin._call.assert_called_with("ClearPreview", None, None)

    def test_search(self):
        list(self.plugin.search(""))
        assert not list(self.plugin.search("x"))
