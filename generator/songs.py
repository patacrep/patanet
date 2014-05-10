# -*- coding: utf-8 -*-
# Copyright (c) 2014 The songbook Team
#
# This program is distributed under the terms of the GNU General
# Public License as published by the Free Software Foundation;
# either version 2 of the License, or any later version.
# For more information, see the file LICENCE.txt
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
