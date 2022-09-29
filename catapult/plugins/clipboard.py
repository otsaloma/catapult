# -*- coding: utf-8 -*-

# Copyright (C) 2022 Osmo Salomaa
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

from catapult.api import copy_text_to_clipboard
from catapult.api import lookup_icon
from catapult.api import Plugin
from catapult.api import PreferencesItem
from catapult.api import SearchResult
from catapult.i18n import _
from gi.repository import Gdk
from gi.repository import Gtk


class ClipboardTrigger(PreferencesItem):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = Gtk.Label(label=_("Trigger"))
        self.widget = Gtk.Entry()

    def dump(self, window):
        value = self.conf.trigger
        self.widget.set_text(value)

    def load(self, window):
        if value := self.widget.get_text().strip():
            self.conf.trigger = value


class ClipboardPlugin(Plugin):

    conf_defaults = {"trigger": "cc"}
    preferences_items = [ClipboardTrigger]
    save_history = False
    title = _("Clipboard")

    def __init__(self):
        super().__init__()
        self._index = {}
        self._clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self._clipboard.connect("owner-change", self._on_clipboard_owner_change)

    def _get_blurb(self, text):
        lines = text.strip().splitlines()
        if len(lines) == 1:
            return lines[0][:100]
        return f"{lines[0]} +{len(lines)-1}"[:100]

    def launch(self, window, id):
        self.debug(f"Copying {id!r} to the clipboard")
        copy_text_to_clipboard(self._index[id])

    def _on_clipboard_owner_change(self, *args):
        if text := self._clipboard.wait_for_text():
            self.debug("Clipboard content changed")
            id = max(self._index.keys(), default=0) + 1
            self._index[id] = text

    def on_window_hide(self):
        # Limit the length of history kept.
        for id in sorted(self._index.keys())[:-100]:
            del self._index[id]

    def search(self, query):
        query = query.lower().strip()
        if query != self.conf.trigger: return
        prev_text = ""
        for i, id in enumerate(reversed(self._index.keys())):
            if self._index[id] == prev_text: continue
            blurb = self._get_blurb(self._index[id])
            prev_text = self._index[id]
            yield SearchResult(
                description=self.title,
                fuzzy=False,
                icon=lookup_icon("printer", "text-x-generic"),
                id=id,
                offset=0,
                plugin=self,
                score=2*0.9**i,
                title=blurb,
            )
