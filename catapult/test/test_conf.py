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
import tempfile


class TestConfigurationStore(catapult.test.TestCase):

    def setup_method(self, method):
        self.conf = catapult.ConfigurationStore()
        handle, self.temp_path = tempfile.mkstemp(prefix="catapult-", suffix=".json")
        self.conf.path = self.temp_path

    def teardown_method(self, method):
        os.remove(self.temp_path)

    def test_read_write(self):
        self.conf.input_font = "1"
        self.conf.theme = "1"
        self.conf.write()
        self.conf.input_font = "2"
        self.conf.theme = "2"
        self.conf.read()
        assert self.conf.input_font == "1"
        assert self.conf.theme == "1"
