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
Functions for song file (.sg) management.
"""
from django.utils.text import slugify
from django.utils.encoding import smart_text
from django.conf.global_settings import LANGUAGES

from patacrep.plastex import parsetex

from generator.models import Song, Artist

import re
import os
import sys
import pprint
import logging

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

LOGGER = logging.getLogger(__name__)

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

def import_song(repo, filepath):
    '''Import a song in the database'''
    data = parsetex(filepath)
    LOGGER.info("Processing " + 
                pprint.pformat(data['titles'][0]))

    artist_name = smart_text(data['args']['by'], 'utf-8')
    artist_slug = slugify(artist_name)

    artist_model, created = Artist.objects.get_or_create(
                            slug=artist_slug,
                            defaults={'name': artist_name}
                            )
    if not created:
        if (artist_model.name != artist_name):
            LOGGER.warning(
                "*** Artist name differs though "
                "slugs are equal : "
                + artist_name + " / "
                + artist_model.name)

    if (len(data['languages']) > 1):
        LOGGER.warning("*** Multiple languages "
                        "in song file; we though"
                        " only support one. "
                        "Picking any.")
    if (len(data['languages']) > 0):
        language_name = data["languages"].pop()
        language_code = next(
                    (x for x in LANGUAGES
                     if x[1].lower() == language_name.lower()
                     ),
                    ('', '')
                     )[0]
        if language_code == '':
            LOGGER.warning("*** No code found for "
                    "language : '" + language_name + "'")

    song_title = smart_text(data['titles'][0], 'utf-8')
    song_slug = slugify(song_title)

    object_hash = repo.git.hash_object(filepath)
    SONG_DIR = os.path.join(repo.working_dir, "songs")
    filepath_rel = os.path.relpath(filepath, SONG_DIR)

    import random

    # For some reason - probably after having interrupted
    # the generation - insertion fails because slug is
    # empty, and there is already an empty one.
    # We assign here a random value, that gets overwritten
    # afterwards.
    song_model, created = Song.objects.get_or_create(
                            title=song_title,
                            artist=artist_model,
                            defaults={
                            'title': song_title,
                            'language': language_code,
                            'file_path': filepath_rel,
                            'slug': ('%06x' % random.randrange(16**6)) })
    if created:
        if Song.objects.filter(slug=song_slug).exists():
            song_slug += '-' + str(song_model.id)
        song_model.slug = song_slug

    else:
        LOGGER.info("-> Already exists.")

    artist_model.save()
    song_model.object_hash = object_hash
    song_model.save()
