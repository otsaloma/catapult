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
import re
import subprocess

from catapult.i18n import _
from gi.repository import Gtk

COMMAND = " ".join((
    "qalc",
    "-s 'decimal comma off'",
    "-s 'precision 6'",
    "-s 'save definitions no'",
    "-s 'save mode no'",
    "-s 'unicode on'",
    "-s 'update exchange rates 0'",
    "'{}'",
))

PATTERN = "^({})".format("|".join((
    r"-?\.?\d",  # Number
    r"\(",       # Parenthesis
    r"(e|pi)\b", # Constant
    r"\w+\(",    # Function call
)))


class CalculatorToggle(catapult.PreferencesItem):

    def __init__(self):
        self.label = Gtk.Label(label=_("Calculator plugin"))
        self.widget = Gtk.Switch()

    def dump(self, window):
        active = "calculator" in catapult.conf.plugins
        self.widget.set_active(active)

    def load(self, window):
        active = self.widget.get_active()
        self.set_plugin_active(window, "calculator", active)


PREFERENCES_ITEMS = [CalculatorToggle]


class CalculatorPlugin(catapult.Plugin):

    save_history = False

    def launch(self, window, id):
        self.debug(f"Copying {id!r} to the clipboard")
        catapult.util.copy_text_to_clipboard(id)

    def search(self, query):
        query = query.strip()
        if re.match(PATTERN, query) is None: return
        command = COMMAND.format(query.replace("'", r"\'"))
        process = subprocess.run(command, shell=True, capture_output=True)
        output = process.stdout.decode("utf-8")
        if not output: return
        self.debug(f"Got {output!r} for {query!r}")
        output = output.splitlines()[0].strip()
        if output.startswith("error:"): return
        if output.startswith("warning:"): return
        expression, result = re.split(r" [=≈] ", output, maxsplit=1)
        yield catapult.SearchResult(
            description=expression,
            fuzzy=False,
            icon=catapult.util.lookup_icon(
                "org.gnome.Calculator",
                "application-x-executable",
            ),
            id=result,
            offset=0,
            plugin=self,
            score=2,
            title=result,
        )
