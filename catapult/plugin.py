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

from catapult.i18n import _
from threading import Thread

class Plugin(catapult.DebugMixin):

    # conf is on purpose at class-level so that it's available,
    # e.g. in the preferences dialog, without class instantiation.
    conf = None
    conf_defaults = {}
    preferences_items = []
    save_history = True
    title = _("Untitled")

    def __init__(self):
        self.ensure_configuration()

    def delete(self, window, id):
        # True if id was deleted, False if not.
        return False

    @classmethod
    def ensure_configuration(cls):
        if cls.conf: return
        cls.read_configuration()

    @classmethod
    def get_name(cls):
        return cls.__module__.split(".")[-1]

    def launch(self, window, id):
        raise NotImplementedError

    @property
    def name(self):
        return self.get_name()

    def on_window_hide(self):
        pass

    def on_window_show(self):
        pass

    @classmethod
    def read_configuration(cls):
        if not cls.conf_defaults: return
        cls.conf = catapult.PluginConfigurationStore(
            cls.get_name(), cls.conf_defaults)
        cls.conf.read()

    def search(self, query):
        raise NotImplementedError

    def update(self):
        pass

    def update_async(self):
        Thread(target=self.update, daemon=True).start()
