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
import logging
import time

START = time.time()


class DebugMixin:

    def debug(self, message):
        logging.debug(f"{self.__class__.__name__}: {message}")

    def tick(self):
        self.__tick = time.time()

    def tock(self):
        return 1000 * (time.time() - self.__tick)


class WindowMixin:

    def set_position_offset(self, xoffset, yoffset):
        self._monitor = catapult.util.get_monitor()
        window_width, window_height = self.get_default_size()
        screen_width, screen_height = catapult.util.get_screen_size(self._monitor)
        x = int(xoffset * (screen_width - window_width))
        y = int(yoffset * screen_height)
        self._position = (x, y)
        # XXX: Gone in GTK4 -- Remove the whole WindowMixin?
        # self.move(x, y)
