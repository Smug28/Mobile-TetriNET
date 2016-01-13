# -*- coding: utf-8 -*-
"""
Mobile TetriNET - TetriNET Client for Android
Copyright (C) 2012-2013  Jiří 'Smuggler' Vaculík

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
# Languages
# Seznam jazyků
LANGUAGES = {
"en": "English",
"cs": "Čeština"
}

# Cesta k souborům s jazyky
STRINGS_PATH = "languages/{0}_strings.txt"

# Třída pro import řetězcu z jazykových souborů
class Strings:
    def __init__(self, lang):
        try:
            strings = open(STRINGS_PATH.format(lang), "r")
            while True:
                s = strings.readline()
                if s != "":
                    code = "self."+s.strip()
                    exec(code)
                else: break
        except:
            return None
        