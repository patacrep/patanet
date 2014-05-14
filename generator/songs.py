# -*- coding: utf-8 -*-
#    Copyright (C) 2014 The Songbook Team
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Functions for song conversion from .sg format to HTML format.
"""

import re

_BLOCKS_PATTERNS = [(r"\beginverse", '<p class="verse" >'),
                    (r"\begin{verse}", '<p class="verse" >'),
                    (r"\beginverse*", '<p class="verse_star" >'),
                    (r"\begin{verse*}", '<p class="verse_star" >'),
                    (r"\beginchorus", '<p class="chorus" >'),
                    (r"\begin{chorus}", '<p class="chorus" >'),
                    ]

_BLOCKS_PATTERNS += [(r"\endverse", '</p>'),
                    (r"\end{verse}", '</p>'),
                    (r"\end{verse*}", '</p>'),
                    (r"\end{chorus}", '</p>'),
                    ]


def parse_chords(content):
    content = re.sub('\\\\\\[(.*?)\]({[^\\\\\s\n]*}|[^\\\\\s\n]*)',
            '<span class="chord"><span class="chord-name">\g<1></span>'
            '<span class="chord-text">\g<2></span></span>',
            content)
    content = content.replace('&', "♭")
    content = content.replace('#', "♯&nbsp")
    return content


def parse_blocks(content):
    for TeX, HTML in _BLOCKS_PATTERNS:
        content = content.replace(TeX, HTML)
    return content


def parse_unsuported(content):
    # remove the beggining of the song
    content = re.sub('^(.*?)<p', '<p', content, flags=re.DOTALL)

    # remove all other commands
    content = re.sub(r'\\(\w*)[(.*)]{(.*)}', '', content)
    content = re.sub(r'\\(\w*){(.*)}', '', content)
    content = re.sub(r'\\(\w*)', '', content)

    content = re.sub(r'{|}', '', content)
    return content


def parse_song(content):
    content = parse_blocks(content)
    content = parse_chords(content)
    content = parse_unsuported(content)
    return content
