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

import shutil
import subprocess

from catapult.api import copy_text_to_clipboard
from catapult.api import lookup_icon
from catapult.api import Plugin
from catapult.api import PreferencesItem
from catapult.api import SearchResult
from catapult.i18n import _
from catapult.i18n import __
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import Gtk

SOURCES = ["gnome-shell", "gpaste"]

class ClipboardSource(PreferencesItem):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = Gtk.Label(label=_("Source"))
        self.widget = Gtk.ComboBoxText.new()
        for source in SOURCES:
            self.widget.append_text(source)

    def dump(self, window):
        value = self.conf.source
        index = SOURCES.index(value) if value in SOURCES else 0
        self.widget.set_active(index)

    def load(self, window):
        index = self.widget.get_active()
        value = SOURCES[index]
        self.conf.source = value

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

    conf_defaults = {"source": "gnome-shell", "trigger": "cc"}
    preferences_items = [ClipboardSource, ClipboardTrigger]
    save_history = False
    title = __("Clipboard")

    def __init__(self):
        super().__init__()
        self._index = {}

    def _call(self, method, parameters, reply_type):
        # See data/gnome-shell/catapult-clipboard@otsaloma.io.
        try:
            bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
            return bus.call_sync("org.gnome.Shell",
                                 "/org/gnome/Shell/Extensions/CatapultClipboard",
                                 "org.gnome.Shell.Extensions.CatapultClipboard",
                                 method,
                                 parameters,
                                 reply_type,
                                 Gio.DBusCallFlags.NONE,
                                 1000,
                                 None)

        except GLib.Error as error:
            self.debug(f"Failed to call {method}: {error.message}")
            return None

    def _get_blurb(self, text):
        text = text.strip()
        if not text: return ""
        text = text.replace("\t", "⟶")
        lines = [x.strip() for x in text.splitlines()]
        # Avoid a very minimal blurb, such as '{' when copying JSON.
        while (len(lines) > 1 and
               len(lines[0]) < 16 and
               not any(x.isalnum() for x in lines[0])):
            lines[0] += " " + lines.pop(1)
        if len(lines) == 1:
            return lines[0][:100]
        return f"{lines[0]}  +{len(lines)-1}"[:100]

    def get_info(self):
        n = len(self.list_history())
        info = _("{} items in clipboard history").format(n)
        if self.conf.source == "gnome-shell":
            return "\n".join((
                info,
                _("Requires GNOME Shell"),
                _("And the Catapult Clipboard extension")))
        return info

    def delete(self, window, id):
        if self.conf.source == "gnome-shell":
            self.debug(f"Deleting {id!r}")
            parameters = GLib.Variant("(t)", (int(id),))
            reply = self._call("Delete", parameters, GLib.VariantType("(b)"))
            return reply is not None and reply.unpack()[0]
        if self.conf.source == "gpaste" and shutil.which("gpaste-client"):
            self.debug(f"Deleting {id!r}")
            command = f"gpaste-client delete {id}"
            completed_process = subprocess.run(command, shell=True)
            return completed_process.returncode == 0

    def launch(self, window, id):
        self.debug(f"Copying {id!r} to the clipboard")
        copy_text_to_clipboard(self._index[id])

    def list_history(self):
        items = {}
        if self.conf.source == "gnome-shell":
            reply = self._call("List", None, GLib.VariantType("(a(ts))"))
            if reply is None: return items
            for id, text in reply.unpack()[0]:
                items[str(id)] = text
        if self.conf.source == "gpaste" and shutil.which("gpaste-client"):
            command = "LANG=C gpaste-client history --zero"
            process = subprocess.run(command, shell=True, capture_output=True)
            output = process.stdout.decode("utf-8")
            for line in output.split("\x00"):
                if len(items) >= 100: break
                if not line.strip(): continue
                id, text = line.split(": ", maxsplit=1)
                if text.startswith("[Files]"): continue
                if text.startswith("[Image,"): continue
                items[id] = text
        return items

    def search(self, query):
        query = query.lower().strip()
        if query != self.conf.trigger: return
        self._index = self.list_history()
        prev_text = ""
        for i, (id, text) in enumerate(self._index.items()):
            if text == prev_text: continue
            prev_text = text
            yield SearchResult(
                description=_(self.title),
                fuzzy=False,
                icon=lookup_icon("printer", "text-x-generic"),
                id=id,
                offset=0,
                plugin=self,
                score=2+1*0.9**i,
                title=self._get_blurb(text),
            )
