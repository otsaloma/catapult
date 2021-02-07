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
import os

DEFAULTS = {
    "theme": "dark",
}


class ConfigurationStore:

    path = os.path.join(catapult.CONFIG_HOME_DIR, "catapult.json")

    def __init__(self):
        for key, value in DEFAULTS.items():
            setattr(self, key, value)

    def read(self):
        if not os.path.isfile(self.path): return
        with open(self.path, "r") as f:
            for key, value in json.load(f).items():
                if key not in DEFAULTS: continue
                setattr(self, key, value)

    def write(self):
        directory = os.path.dirname(self.path)
        os.makedirs(directory, exist_ok=True)
        blob = {x: getattr(self, x) for x in DEFAULTS}
        blob["version"] = catapult.__version__
        blob = json.dumps(blob, ensure_ascii=False, indent=2, sort_keys=True)
        with open(self.path, "w") as f:
            f.write(blob + "\n")
