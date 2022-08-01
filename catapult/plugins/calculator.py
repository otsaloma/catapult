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

import re
import subprocess

from catapult.api import copy_text_to_clipboard
from catapult.api import lookup_icon
from catapult.api import Plugin
from catapult.api import SearchResult
from catapult.i18n import _
from threading import Thread

COMMAND = " ".join((
    "qalc",
    "-s 'decimal comma off'",
    "-s 'fractions off'",
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


class CalculatorPlugin(Plugin):

    save_history = False
    title = _("Calculator")

    def __init__(self):
        super().__init__()
        Thread(target=self.update_exchange_rates, daemon=True).start()

    def launch(self, window, id):
        self.debug(f"Copying {id!r} to the clipboard")
        copy_text_to_clipboard(id)

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
        yield SearchResult(
            description=expression,
            fuzzy=False,
            icon=lookup_icon(
                "org.gnome.Calculator",
                "application-x-executable",
            ),
            id=result,
            offset=0,
            plugin=self,
            score=2,
            title=result,
        )

    def update_exchange_rates(self):
        # Update exchange rates about once a week and check a conversion.
        command = "qalc -s 'update exchange rates 7' '1 USD to EUR'"
        process = subprocess.run(command, shell=True, capture_output=True)
        output = process.stdout.decode("utf-8").strip()
        self.debug(f"Updated exchange rates: {output!r}")
