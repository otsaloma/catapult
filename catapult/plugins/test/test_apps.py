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
import time


class TestAppsPlugin(catapult.test.TestCase):

    def setup_method(self, method):
        self.plugin = catapult.plugins.apps.AppsPlugin()

    def teardown_method(self, method):
        # Wait for threads to terminate.
        time.sleep(1)

    def test_on_window_show(self):
        self.plugin.on_window_show()

    def test_search(self):
        self.plugin.search("t")
        self.plugin.search("te")
        self.plugin.search("tes")
        self.plugin.search("test")
