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
import shutil


class ConfigurationStore(catapult.DebugMixin):

    _defaults = {
        "max_results": 24,
        "max_results_visible": 8,
        "plugins": ["apps", "builtins", "calculator", "files", "session"],
        "theme": "dark",
        "toggle_key": "<Control>space",
    }

    _path = catapult.CONFIG_HOME / "catapult.json"

    def __init__(self):
        self.restore_defaults()

    def read(self):
        if not self._path.exists(): return
        text = self._path.read_text("utf-8")
        data = json.loads(text)
        for key, value in data.items():
            if key not in self._defaults: continue
            setattr(self, key, value)
        self.debug(f"Read configuration from {self._path!s}")
        if data.get("version", "") != catapult.__version__:
            # Take a backup of the config file upon version bump.
            bak = self._path.with_suffix(".json.bak")
            bak.unlink(missing_ok=True)
            shutil.copy2(self._path, bak)
            self.debug(f"Created backup {bak!s}")

    def restore_defaults(self):
        for key, value in self._defaults.items():
            setattr(self, key, value)

    def to_dict(self):
        return copy.deepcopy({x: getattr(self, x) for x in self._defaults})

    def write(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = {x: getattr(self, x) for x in self._defaults}
        for key, value in list(data.items()):
            # Comment out keys with default value.
            if value == self._defaults[key]:
                data[f"# {key}"] = data.pop(key)
        data["version"] = catapult.__version__
        keys = sorted(data, key=lambda x: x.lstrip("# "))
        data = {x: data[x] for x in keys}
        text = json.dumps(data, ensure_ascii=False, indent=2)
        try:
            catapult.util.atomic_write(self._path, text + "\n", "utf-8")
        except OSError as error:
            return print(f"Writing {self._path!s} failed: {str(error)}")
        self.debug(f"Wrote configuration to {self._path!s}")


class PluginConfigurationStore(ConfigurationStore):

    def __init__(self, plugin_name, defaults):
        self._defaults = copy.deepcopy(defaults)
        self._path = catapult.CONFIG_HOME / "plugins" / f"{plugin_name}.json"
        self.restore_defaults()
