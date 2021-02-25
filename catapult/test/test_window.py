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


class TestWindow(catapult.test.TestCase):

    def setup_method(self, method):
        self.window = catapult.Window()

    def test_bind_toggle_key(self):
        self.window.bind_toggle_key("<Shift><Control><Alt>F12")

    def test_get_query(self):
        self.window._input_entry.set_text("test")
        assert self.window.get_query() == "test"

    def test_hide(self):
        self.window.show()
        self.window.hide()

    def test__on_icon_theme_changed(self):
        self.window._icon_theme.emit("changed")

    def test_select_next_result(self):
        self.window.select_next_result()

    def test_select_previous_result(self):
        self.window.select_previous_result()

    def test_show(self):
        self.window.hide()
        self.window.show()

    def test_toggle(self):
        self.window.toggle()
        self.window.toggle()

    def test_unbind_toggle_key(self):
        self.window.unbind_toggle_key()
