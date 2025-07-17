# -*- coding: utf-8 -*-

# Copyright (C) 2025 Osmo Salomaa
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

import cairo
import functools

from catapult.api import copy_text_to_clipboard
from catapult.api import find_split_all
from catapult.api import get_scale_factor
from catapult.api import Plugin
from catapult.api import SearchResult
from catapult.i18n import _
from dataclasses import dataclass
from gi.repository import Pango
from gi.repository import PangoCairo
from pathlib import Path

ICON_TEMPLATE = """
<svg width="48" height="48" xmlns="http://www.w3.org/2000/svg">
  <rect x="5" y="5" width="38" height="38" rx="3" ry="3" fill="white"/>
  <text x="24" y="34" font-family="Noto Sans" font-size="28" text-anchor="middle" fill="black">{}</text>
</svg>
""".strip()

@functools.cache
def get_pango_font(font):
    font_desc = Pango.FontDescription(font)
    font_map = PangoCairo.font_map_get_default()
    context = font_map.create_context()
    return context.load_font(font_desc)

@dataclass
class Block:

    start: int
    end:   int
    name:  str

@dataclass
class Character:

    block: str
    name:  str
    value: str
    terms: str
    search_target: str = ""

    def finalize(self):
        # Make this derived string a proper attribute so that
        # we can search fast without having to rebuild this.
        self.search_target = f"{self.name.lower()} {self.terms.lower()}".strip()

    @property
    def font(self):
        return "Noto Color Emoji" if self.is_emoji else "Noto Sans"

    @property
    def is_emoji(self):
        return self.block in {
            "Dingbats",
            "Emoticons",
            "Miscellaneous Symbols and Pictographs",
            "Miscellaneous Symbols",
            "Supplemental Symbols and Pictographs",
            "Symbols and Pictographs Extended-A",
            "Transport and Map Symbols",
        }

    @property
    def is_supported(self):
        if len(self.value) > 1:
            # Can't check emoji sequences!
            return True
        font = get_pango_font(self.font)
        return font.has_char(self.value)

class CharactersPlugin(Plugin):

    title = _("Characters")

    def __init__(self):
        super().__init__()
        self._blocks = list(self._load_blocks())
        self._blocks.sort(key=lambda x: x.start)
        self.debug(f"Loaded {len(self._blocks)} blocks")
        self._characters = []
        self._characters += list(self._load_emojis())
        self._characters += list(self._load_characters())
        self._characters.sort(key=lambda x: x.value)
        self.debug(f"Loaded {len(self._characters)} characters")
        self.debug("Initialization complete")

    def _find_block(self, code):
        for block in self._blocks:
            if block.start <= code <= block.end:
                return block.name

    def launch(self, window, id):
        self.debug(f"Copying {id!r} to the clipboard")
        copy_text_to_clipboard(id)

    def _load_blocks(self):
        # We're not currently using the block info, but we're including
        # it for completeness, so that it's easy to experiment with
        # filtering out generally uninteresting blocks etc.
        path = Path(__file__).parent / "unicode" / "Blocks.txt"
        for line in path.read_text("utf-8").splitlines():
            line = line.strip()
            if not line: continue
            if line.startswith("#"): continue
            if ".." in line and ";" in line:
                rng, name = line.split(";", 1)
                start, end = rng.split("..")
                start = int(start, 16)
                end = int(end, 16)
                yield Block(start=start, end=end, name=name.strip())

    def _load_characters(self):
        # Skip emojis that were already loaded from emoji-list.
        existing = set(x.value for x in self._characters)
        path = Path(__file__).parent / "unicode" / "UnicodeData.txt"
        for line in path.read_text("utf-8").splitlines():
            line = line.strip()
            if not line: continue
            if line.startswith("#"): continue
            fields = line.split(";")
            code, name, category = fields[:3]
            if category.startswith("C"): continue
            code = int(code, 16)
            value = chr(code)
            if value in existing: continue
            block = self._find_block(code)
            character = Character(block=block,
                                  name=f"UNICODE {name}",
                                  value=value,
                                  terms="")

            if character.is_supported:
                character.finalize()
                yield character

    def _load_emojis(self):
        path = Path(__file__).parent / "unicode" / "emoji-list.txt"
        for line in path.read_text("utf-8").splitlines():
            line = line.strip()
            if not line: continue
            str_codes, name, terms = line.split(";")
            int_codes = []
            for code in str_codes.split():
                assert code.startswith("U+")
                int_codes.append(int(code[2:], 16))
            assert int_codes
            value = "".join(chr(x) for x in int_codes)
            character = Character(block="Emoticons",
                                  name=f"UNICODE {name}",
                                  value=value,
                                  terms=terms)

            if character.is_supported:
                character.finalize()
                yield character

    def _render_cairo_icon(self, character):
        # We need this instead of the simpler ICON_TEMPLATE for emojis,
        # because SVG rendering as done by GdkPixbuf does not support
        # some font features needed by Noto Color Emoji.
        scale_factor = get_scale_factor()
        size = round(48 * scale_factor)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
        ctx = cairo.Context(surface)
        layout = PangoCairo.create_layout(ctx)
        font_size = round(26 * scale_factor)
        font_desc = Pango.FontDescription(f"{character.font} {font_size}")
        layout.set_font_description(font_desc)
        layout.set_text(character.value, -1)
        width, height = layout.get_pixel_size()
        x = round((size - width)  / 2)
        y = round((size - height) / 2)
        ctx.move_to(x, y)
        ctx.set_source_rgba(0, 0, 0, 1)
        PangoCairo.show_layout(ctx, layout)
        return surface

    def search(self, query):
        query = query.lower().strip()
        for i, character in enumerate(self._characters):
            found = find_split_all(query, character.search_target)
            offset = min(found.values())
            if offset < 0: continue
            if character.is_emoji:
                # cairo.ImageSurface
                icon = self._render_cairo_icon(character)
            else:
                # SVG string
                icon = ICON_TEMPLATE.format(character.value)
            yield SearchResult(
                description="".join(f"\\u{ord(x):04x}" for x in character.value),
                fuzzy=False,
                icon=icon,
                id=character.value,
                offset=offset,
                plugin=self,
                score=0.9*0.9**offset,
                title=character.name,
            )
