# -*- coding: utf-8 -*-
#    Copyright (C) 2014 The Patacrep Team
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
Functions for song file (.sgc) rendering.
"""


from patanet.settings import SONGS_LIBRARY_DIR


from patacrep.songs.chordpro import ChordproSong
from patacrep.build import DEFAULT_CONFIG
from patacrep.songs.chordpro import ChordproSong

from pathlib import PurePosixPath

import os

from django.conf import settings


def parse_song(filename):
    """Parse song 'filename', and return the corresponding HTML code."""
    # TODO: Clean this file

    # Hack to read the .sgc file
    filename += "c"

    relpath = os.path.join('songs', filename)

    datadir = settings.SONGS_LIBRARY_DIR
    config = DEFAULT_CONFIG.copy()
    song = ChordproSong(datadir, relpath, config)
    song.parse(config)

    more = {
        'failed': (song.titles == []),
        'cover_url': get_cover_url(song, datadir),
        'chords': get_chords(song.data),
    }

    with open(song.fullpath) as fd:
        more['full_content'] = fd.read()

    setattr(song, 'more', more)
    return song

def get_chords(metadata):
    raw_chords = metadata.get('define', [])
    chords = []

    def string_pos(strings):
        if not strings:
            return ''
        # Need a fix on the JS lib to join with a space
        return ''.join([str(pos) if pos is not None else 'x' for pos in strings])

    for raw_chord in raw_chords:
        chord = {
            'key': raw_chord.key.chord.replace('&', '♭').replace('#','♯'),
            'basefret': raw_chord.basefret if raw_chord.basefret else 0,
            'frets':  string_pos(raw_chord.frets),
            'fingers':  string_pos(raw_chord.fingers),
        }
        chords.append(chord)
    return chords

def get_cover_url(song, datadir):
    cover_file = song.get_cover_fullpath()
    if not cover_file:
        return None
    relfile = str(PurePosixPath(cover_file).relative_to(datadir))
    return relfile
