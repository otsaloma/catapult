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
import copy
import json
import os

DEFAULTS = {
    "apps_scan_interval": 900, # s
    "files_exclude": ["lost+found"],
    "files_include": [os.path.expanduser("~/*")],
    "files_scan_interval": 900, # s
    "max_results": 24,
    "max_results_visible": 8,
    "plugins": ["apps", "builtins", "calculator", "files", "session"],
    "theme": "dark",
    "toggle_key": "<Control>space",
}


class ConfigurationStore(catapult.DebugMixin):

    path = catapult.CONFIG_HOME / "catapult.json"

    def __init__(self):
        for key, value in DEFAULTS.items():
            setattr(self, key, value)

    def read(self):
        if not self.path.exists(): return
        text = self.path.read_text("utf-8")
        for key, value in json.loads(text).items():
            if key not in DEFAULTS: continue
            setattr(self, key, value)
        self.debug("Read configuration")

    def to_dict(self):
        return copy.deepcopy({x: getattr(self, x) for x in DEFAULTS})

    def write(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        blob = {x: getattr(self, x) for x in DEFAULTS}
        for key, value in list(blob.items()):
            # Comment out keys with default value.
            if value == DEFAULTS[key]:
                blob[f"# {key}"] = blob.pop(key)
        blob["version"] = catapult.__version__
        keys = sorted(blob, key=lambda x: x.lstrip("# "))
        blob = {x: blob[x] for x in keys}
        blob = json.dumps(blob, ensure_ascii=False, indent=2)
        try:
            self.path.write_text(blob + "\n", "utf-8")
        except OSError as error:
            return print(f"Writing {str(self.path)} failed: {str(error)}")
        self.debug("Wrote configuration")
