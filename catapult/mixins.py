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
import time

START = time.time()


class DebugMixin:

    def debug(self, *args, **kwargs):
        if not catapult.DEBUG: return
        clock = time.time() - START
        name = self.__class__.__name__
        print(f"{clock:.3f} {name}:", *args, **kwargs)

    def tick(self):
        self.__tick = time.time()

    def tock(self):
        return 1000 * (time.time() - self.__tick)


class WindowMixin:

    def set_position_offset(self, xoffset, yoffset):
        self._monitor = catapult.util.get_monitor()
        self._monitor_was_primary = self._monitor.is_primary()
        window_width, window_height = self.get_size()
        screen_width, screen_height = catapult.util.get_screen_size(self._monitor)
        x = int(xoffset * (screen_width - window_width))
        y = int(yoffset * screen_height)
        self._position = (x, y)
        # Moving a window will not work with all window managers.
        # On stock GNOME, it works with X, not with Wayland.
        self.move(x, y)
