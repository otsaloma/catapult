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

import catapult.test


class TestCalculatorPlugin(catapult.test.TestCase):

    def setup_method(self, method):
        self.plugin = catapult.plugins.calculator.CalculatorPlugin()

    def test_search_constant(self):
        result = next(self.plugin.search("pi*2"))
        assert result.description in ["pi * 2", "pi × 2"]
        assert result.title == "6.28319"

    def test_search_function(self):
        result = next(self.plugin.search("sqrt(2)"))
        assert result.description == "sqrt(2)"
        assert result.title == "1.41421"

    def test_search_numbers(self):
        result = next(self.plugin.search("1+2"))
        assert result.description == "1 + 2"
        assert result.title == "3"

    def test_search_parentheses(self):
        result = next(self.plugin.search("(2+2)*(2+2)"))
        assert result.description in ["(2 + 2) * (2 + 2)", "(2 + 2) × (2 + 2)"]
        assert result.title == "16"

    def test_search_unit_conversion(self):
        result = next(self.plugin.search("1 mi to km"))
        assert result.description in ["1 * mile", "1 × mile"]
        assert result.title == "1.60934 km"
