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

import subprocess

from catapult.api import find_split_all
from catapult.api import get_desktop_environment
from catapult.api import Plugin
from catapult.api import SearchResult
from catapult.i18n import _

def split(title):
    return [x.strip() for x in title.split(";") if x.strip()]

ACTIONS = [{
    "desktops": ["GNOME"],
    # TRANSLATORS: Include all possible variations separated by semicolons.
    "titles":   split(_("Lock Screen")),
    "command":  "xdg-screensaver lock",
}, {
    "desktops": ["GNOME"],
    # TRANSLATORS: Include all possible variations separated by semicolons.
    "titles":   split(_("Log Out;Log Off")),
    "command":  "gnome-session-quit --logout",
}, {
    "desktops": ["GNOME"],
    # TRANSLATORS: Include all possible variations separated by semicolons.
    "titles":   split(_("Power Off;Shutdown")),
    "command":  "gnome-session-quit --power-off",
}, {
    "desktops": ["GNOME"],
    # TRANSLATORS: Include all possible variations separated by semicolons.
    "titles":   split(_("Reboot;Restart")),
    "command":  "gnome-session-quit --reboot",
}]

class SessionPlugin(Plugin):

    title = _("Session")

    def get_info(self):
        desktops = [y for x in ACTIONS for y in x["desktops"]]
        desktops = "\n".join(sorted(set(desktops)))
        return "\n".join((_("Supported desktops:"), desktops))

    def launch(self, window, id):
        self.debug(f"Launching {id}")
        subprocess.run(id, shell=True)

    def search(self, query):
        query = query.lower().strip()
        desktop = get_desktop_environment()
        for action in ACTIONS:
            if desktop not in action["desktops"]: continue
            founds = [find_split_all(query, x.lower()) for x in action["titles"]]
            offsets = [min(x.values()) for x in founds]
            offsets = [x for x in offsets if x >= 0]
            if not offsets: continue
            title = action["titles"][0]
            self.debug(f"Found {title} for {query!r}")
            yield SearchResult(
                description=action["command"],
                fuzzy=False,
                icon="application-x-executable",
                id=action["command"],
                offset=min(offsets),
                plugin=self,
                score=1,
                title=title,
            )
