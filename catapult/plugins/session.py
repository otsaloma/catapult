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
import subprocess

from catapult.i18n import _

COMMANDS = {
    "GNOME": {
        "lock-screen": "gnome-screensaver-command --lock",
        "log-out": "gnome-session-quit --logout",
        "power-off": "gnome-session-quit --power-off",
        "reboot": "gnome-session-quit --reboot",
    },
}

TITLES = {
    "lock-screen": _("Lock Screen"),
    "log-out": _("Log Out"),
    "power-off": _("Power Off"),
    "reboot": _("Reboot"),
}


class SessionPlugin(catapult.Plugin):

    def __init__(self):
        super().__init__()
        self.debug("Initialization complete")

    def launch(self, id):
        desktop = catapult.util.get_desktop_environment()
        command = COMMANDS[desktop][id]
        self.debug(f"Launching {command}")
        subprocess.run(command, shell=True)

    def search(self, query):
        query = query.lower().strip()
        desktop = catapult.util.get_desktop_environment()
        if desktop not in COMMANDS: return
        for key, title in TITLES.items():
            offset = title.lower().find(query)
            if offset < 0: continue
            self.debug(f"Found {title} for {query!r}")
            yield catapult.SearchResult(
                description=COMMANDS[desktop][key],
                fuzzy=False,
                icon=catapult.util.lookup_icon("application-x-executable"),
                id=key,
                offset=offset,
                plugin=self,
                score=1,
                title=title,
            )
