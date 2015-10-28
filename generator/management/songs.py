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
Songs management utilities
"""
from django.utils.text import slugify
from django.db import transaction

from generator.models import Song, Artist

import pygit2 as git
import logging

LOGGER = logging.getLogger(__name__)

@transaction.atomic
def import_songs(metadata):
    """Import all the metadata into the database"""
    catalog = Catalog()
    songs = []
    for song in metadata:
        title = song['titles'][0]
        file_path = song['filepath']

        if file_path in catalog.filepaths:
            LOGGER.info("Skip: " + title
                + "\t\t\t\t\t- Already in Database")
            continue

        slug = catalog.get_song_slug(title)
        artist_id = catalog.get_artist_id(song['authors'][0])
        language = song['lang']
        object_hash = git.hashfile(song['fullpath'])

        data = {}
        for i in (
            'title', 'file_path',
            'slug', 'artist_id',
            'language', 'object_hash',
            ):
            data[i] = locals()[i]

        model = Song(**data)
        LOGGER.info("Add: " + title)
        songs.append(model)

    Song.objects.bulk_create(songs)
    LOGGER.info(
        " -> " +
        str(len(songs)) + 
        " songs added to the db")

class Catalog:
    """Class used to efficiently compute slugs and prevent database collision"""
    def __init__(self):
        self._init_songs()
        self._init_artists()

    def _init_songs(self):
        songs = Song.objects.values_list('file_path', 'slug')
        if not songs:
            self.filepaths = set()
            self.song_slugs = set()
        else:
            self.filepaths, self.song_slugs = map(set, zip(*songs))

    def get_song_slug(self, title):
        slug = slugify(title)
        if slug in self.song_slugs:
            i = 1
            tmp_slug = slug + '-' + str(i)
            while tmp_slug in self.song_slugs:
                i += 1
                tmp_slug = slug + '-' + str(i)

            LOGGER.info(
                "SlugCollision: "
                + slug + ". Use "
                + tmp_slug + " instead for " + title)
            slug = tmp_slug

        self.song_slugs.add(slug)
        return slug

    def _init_artists(self):
        artists = Artist.objects.values_list('id', 'slug', 'name')
        self.artists = { slug: (id, name) for id, slug, name in artists }

    def get_artist_name(self, name_tuple):
        last_name, first_name = name_tuple
        if first_name:
            artist_name = first_name + ' ' + last_name
        else:
            artist_name = last_name

        return artist_name

    def get_artist_id(self, name_tuple):
        artist_name = self.get_artist_name(name_tuple)
        artist_slug = slugify(artist_name)

        try:
            id, name = self.artists[artist_slug]
            if (name != artist_name):
                LOGGER.warning(
                    "*** Artist name differs though "
                    "slugs are equal : "
                    + artist_name + " / " + name)
            return id
        except KeyError:
            model = Artist.objects.create(
                            slug=artist_slug,
                            name=artist_name,
                            )
            self.artists[artist_slug] = model.id, artist_name
            return model.id
