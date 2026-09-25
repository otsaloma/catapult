# -*- coding: utf-8 -*-

# Copyright (C) 2026 Osmo Salomaa
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

from catapult.api import Plugin
from catapult.api import SearchResult
from catapult.i18n import _
from catapult.i18n import __
from gi.repository import Gio
from gi.repository import GLib

class WindowsPlugin(Plugin):

    save_history = False
    title = __("Windows")

    def __init__(self):
        super().__init__()
        self._previewing = False

    def _call(self, method, parameters, reply_type):
        # See data/gnome-shell/catapult-windows@otsaloma.io.
        try:
            bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
            reply = bus.call_sync("org.gnome.Shell",
                                  "/org/gnome/Shell/Extensions/CatapultWindows",
                                  "org.gnome.Shell.Extensions.CatapultWindows",
                                  method,
                                  parameters,
                                  reply_type,
                                  Gio.DBusCallFlags.NONE,
                                  1000,
                                  None)

            # Without a reply type, the reply is an empty tuple, which
            # is falsy, so return True to mark success.
            return reply if reply_type else True
        except GLib.Error as error:
            self.debug(f"Failed to call {method}: {error.message}")
            return None

    @classmethod
    def get_static_info(cls):
        return "\n".join((
            _("Requires GNOME Shell"),
            _("And the Catapult Windows extension")))

    def launch(self, window, id):
        self.debug(f"Activating window {id}")
        self._call("Activate", GLib.Variant("(t)", (int(id),)), None)

    def on_result_selected(self, result):
        if result is None or result.plugin is not self:
            return self.on_window_hide()
        if self._call("Preview", GLib.Variant("(t)", (int(result.id),)), None):
            self._previewing = True

    def on_window_hide(self):
        if not self._previewing: return
        self._previewing = False
        self._call("ClearPreview", None, None)

    def search(self, query):
        # Only list windows on a blank query, i.e. before typing anything.
        if query: return
        reply = self._call("List", None, GLib.VariantType("(a(tsss))"))
        if reply is None: return
        windows = [x for x in reply.unpack()[0] if x[2] != "io.otsaloma.catapult.desktop"]
        for i, (id, title, app_id, app_name) in enumerate(windows):
            try:
                app = Gio.DesktopAppInfo.new(app_id)
            except TypeError:
                # The app ID may not resolve to a desktop file.
                app = None
            yield SearchResult(
                description=app_name,
                fuzzy=False,
                icon=(app and app.get_icon()) or "application-x-executable",
                id=str(id),
                offset=0,
                plugin=self,
                score=0.9**i,
                title=title,
            )
