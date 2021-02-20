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

import catapult
import json

DEFAULTS = {
    "files_exclude": [],
    "files_include": ["~/*"],
    "files_scan_interval": 900, # s
    "max_results": 24,
    "max_results_visible": 8,
    "plugins": ["apps", "files"],
    "theme": "dark",
    "toggle_key": "<Control>space",
}


class ConfigurationStore:

    path = catapult.CONFIG_HOME / "catapult.json"

    def __init__(self):
        for key, value in DEFAULTS.items():
            setattr(self, key, value)

    def read(self):
        if not self.path.exists(): return
        with open(self.path, "r") as f:
            for key, value in json.load(f).items():
                if key not in DEFAULTS: continue
                setattr(self, key, value)

    def write(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        blob = {x: getattr(self, x) for x in DEFAULTS}
        for key, value in list(blob.items()):
            # Comment out keys with default value.
            if value == DEFAULTS[key]:
                blob[f"# {key}"] = blob.pop(key)
        blob["version"] = catapult.__version__
        blob = json.dumps(blob, ensure_ascii=False, indent=2, sort_keys=True)
        with open(self.path, "w") as f:
            f.write(blob + "\n")
