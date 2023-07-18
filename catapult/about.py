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

from catapult.i18n  import _
from gi.repository import GObject
from gi.repository import Gtk


class AboutDialog(Gtk.AboutDialog):

    def __init__(self, parent):
        GObject.GObject.__init__(self)
        self.set_artists(("Osmo Salomaa <otsaloma@iki.fi>",))
        self.set_authors(("Osmo Salomaa <otsaloma@iki.fi>",))
        self.set_comments(_("App launcher"))
        self.set_copyright("Copyright © 2021–2023 Osmo Salomaa")
        self.set_license_type(Gtk.License.GPL_3_0)
        self.set_logo_icon_name("io.otsaloma.catapult")
        self.set_program_name("Catapult")
        self.set_title(_("About Catapult"))
        self.set_version(catapult.__version__)
        self.set_website("https://otsaloma.io/catapult")
        self.set_website_label("https://otsaloma.io/catapult")

        # TRANSLATORS: This is a special message that shouldn't be translated
        # literally. It is used in the about dialog to give credits to the
        # translators. Thus, you should translate it to your name and email
        # address. You can also include other translators who have contributed
        # to this translation; in that case, please write them on separate
        # lines seperated by newlines (\n).
        self.set_translator_credits(_("translator-credits"))
