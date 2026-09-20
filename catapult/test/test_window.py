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

from unittest.mock import Mock

class TestWindow(catapult.test.TestCase):

    def setup_method(self, method):
        self.window = catapult.Window()

    def test_activate_deactivate_plugin(self):
        self.window.activate_plugin("apps")
        self.window.deactivate_plugin("apps")
        self.window.activate_plugin("apps")
        self.window.deactivate_plugin("apps")

    def test_get_query(self):
        self.window._input_entry.set_text("test")
        assert self.window.get_query() == "test"

    def test_hide(self):
        self.window.show()
        self.window.hide()

    def test__on_gesture_pressed(self):
        entry = self.window._input_entry
        input_box = entry.get_parent()
        gesture = Mock()
        for picked, expected in (
            (entry, "query"),
            (entry.get_first_child(), "query"),
            (input_box, ":"),
            (input_box.get_first_child(), ":"),
            (None, ":"),
        ):
            entry.set_text("query")
            gesture.get_widget.return_value.pick.return_value = picked
            self.window._on_gesture_pressed(gesture, 1, 0, 0)
            assert self.window.get_query() == expected

    def test__on_icon_theme_changed(self):
        self.window._icon_theme.emit("changed")

    def test_result_selection(self):
        self.window._plugins = []
        self.window._scroll_to_row = Mock()
        result = Mock(icon="", title="Window", description="")
        self.window._search_manager.search = Mock(return_value=[result])
        self.window.show()
        assert self.window._result_list.get_selected_row() is None
        self.window.select_next_result()
        assert self.window._result_list.get_selected_row() is self.window._result_rows[0]
        self.window.select_previous_result()
        assert self.window._result_list.get_selected_row() is None
        self.window._input_entry.set_text("query")
        self.window._on_input_entry_notify_text_do()
        assert self.window._result_list.get_selected_row() is self.window._result_rows[0]

    def test_select_next_result(self):
        self.window.select_next_result()

    def test_select_previous_result(self):
        self.window.select_previous_result()

    def test_set_plugin_active(self):
        self.window.set_plugin_active("apps", True)
        self.window.set_plugin_active("apps", False)
        self.window.set_plugin_active("apps", True)
        self.window.set_plugin_active("apps", False)

    def test_show(self):
        self.window.hide()
        self.window.show()

    def test_toggle(self):
        self.window.toggle()
        self.window.toggle()
