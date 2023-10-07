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
import json
import os
import tempfile

from pathlib import Path
from unittest.mock import patch

class TestConfigurationStore(catapult.test.TestCase):

    def setup_method(self, method):
        handle, self.temp_path = tempfile.mkstemp(suffix=".json")
        self.conf = catapult.ConfigurationStore(self.temp_path)

    def teardown_method(self, method):
        os.remove(self.temp_path)

    def test_migrate_0_3(self):
        config_home = Path(tempfile.mkdtemp())
        with patch("catapult.CONFIG_HOME", config_home):
            data = {
                "apps_scan_interval": 100,
                "files_exclude": ["test"],
                "files_include": ["rest"],
                "files_scan_interval": 200,
                "version": "0.2",
            }
            text = json.dumps(data, ensure_ascii=False, indent=2)
            path = config_home / "catapult.json"
            path.write_text(text, "utf-8")
            conf = catapult.ConfigurationStore()
            conf.read()
            assert config_home.joinpath("catapult.json.bak").exists()
            # Keys separated into plugins/apps.json.
            path = config_home / "plugins" / "apps.json"
            data = json.loads(path.read_text("utf-8"))
            assert data == {
                "scan_interval": 100,
            }
            # Keys separated into plugins/files.json.
            path = config_home / "plugins" / "files.json"
            data = json.loads(path.read_text("utf-8"))
            assert data == {
                "exclude": ["test"],
                "include": ["rest"],
                "scan_interval": 200,
            }
        config_home.joinpath("plugins", "apps.json").unlink()
        config_home.joinpath("plugins", "files.json").unlink()
        config_home.joinpath("plugins").rmdir()
        config_home.joinpath("catapult.json").unlink()
        config_home.joinpath("catapult.json.bak").unlink()
        config_home.rmdir()

    def test_read_write(self):
        self.conf.theme = "1"
        self.conf.write()
        self.conf.theme = "2"
        self.conf.read()
        assert self.conf.theme == "1"

    def test_to_dict(self):
        assert self.conf.to_dict()

class TestPluginConfigurationStore(TestConfigurationStore):

    def setup_method(self, method):
        self.conf = catapult.PluginConfigurationStore("test", {"x": 1})
        handle, self.temp_path = tempfile.mkstemp(suffix=".json")
        self.conf._path = Path(self.temp_path)

    def test_read_write(self):
        self.conf.x = 111
        self.conf.write()
        self.conf.x = 222
        self.conf.read()
        assert self.conf.x == 111
