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
    song_model = ChordproSong(datadir, relpath, config)
    song_model.parse(config)
    failed = song_model.titles == []


    metadata = song_model.data

    basedir = os.path.dirname(song_model.fullpath)

    song = {
        'album': get_data(metadata, 'album'),
        'cover_url': get_cover_url(metadata, basedir, datadir),
        'url': get_data(metadata, 'url'),
        'chords': get_chords(metadata),
        'fullpath': song_model.fullpath,
        'capo': None, #Not implemented by patacrep yet
        'languages': song_model.languages,
    }


    if failed:
        song['failed'] = True

    with open(song['fullpath']) as fd:
        song['full_content'] = fd.read()
    return song

def get_data(metadata, key, default=None):
    if key in metadata:
        return metadata[key]
    return default

def get_chords(metadata):
    raw_chords = get_data(metadata, 'define', [])
    chords = []

    def string_pos(strings):
        if not strings:
            return ''
        # Need a fix on the JS lib to join with a space
        return ''.join([str(pos) if pos else 'x' for pos in strings])

    for raw_chord in raw_chords:
        chord = {
            'key': raw_chord.key.chord,
            'basefret': raw_chord.basefret if raw_chord.basefret else 0,
            'frets':  string_pos(raw_chord.frets),
            'fingers':  string_pos(raw_chord.fingers),
        }
        chords.append(chord)
    return chords

def get_cover_path(file_without_ext):
    exts = ['', '.jpg', '.png']
    for ext in exts:
        print(file_without_ext + ext)
        if os.path.isfile(file_without_ext + ext):
            return file_without_ext + ext
    raise FileNotFoundError()

def get_cover_url(metadata, basedir, datadir):
    cov = get_data(metadata, 'cov')
    if not cov:
        return None
    cover_without_ext = os.path.join(basedir, str(cov))
    coverfile = get_cover_path(cover_without_ext)
    relfile = str(PurePosixPath(coverfile).relative_to(datadir))
    return relfile
