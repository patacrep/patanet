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


from django.core.management.base import BaseCommand
from django.conf import settings
from songbook_core.plastex import parsetex
import pprint
import git
import os
from generator.models import Song, Artist
from django.db import transaction
from django.utils.text import slugify
from django.utils.encoding import smart_text
from django.conf.global_settings import LANGUAGES


def _file_error(error):
    print(error)


SONGS_DIR = os.path.join(settings.SONGS_LIBRARY_DIR, "songs")


@transaction.atomic
class Command(BaseCommand):
    args = ""
    help = "Import song information into db"

    def handle(self, *args, **options):

        repo = git.Repo(settings.SONGS_LIBRARY_DIR)
        gitcmd = repo.git

        for root, _dirs, filenames in os.walk(SONGS_DIR,
                                             topdown=True,
                                             onerror=_file_error,
                                             followlinks=False):

            for filename in filenames:
                if filename.lower().endswith(".sg"):
                    filepath = os.path.realpath(os.path.join(root, filename))
                    filepath_rel = os.path.relpath(
                                        filepath,
                                        SONGS_DIR)
                    try:
                        data = parsetex(filepath)
                        self.stdout.write("Processing " +
                                          pprint.pformat(data['titles'][0]))

                        artist_name = smart_text(data['args']['by'], 'utf-8')
                        artist_slug = slugify(artist_name)

                        artist_model, created = Artist.objects.get_or_create(
                                                slug=artist_slug,
                                                defaults={'name': artist_name}
                                                )
                        if not created:
                            if (artist_model.name != artist_name):
                                self.stderr.write(
                                    "*** Artist name differs though "
                                    "slugs are equal : "
                                    + artist_name + " / "
                                    + artist_model.name)

                        if (len(data['languages']) > 1):
                            self.stderr.write("*** Multiple languages " +
                                              "in song file; we though" +
                                              " only support one. " +
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
                                self.stderr.write("*** No code found for "
                                        "language : '" + language_name + "'")

                        song_title = smart_text(data['titles'][0], 'utf-8')
                        song_slug = slugify(song_title)

                        object_hash = gitcmd.hash_object(filepath)

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
                                                'object_hash': object_hash,
                                                'file_path': filepath_rel,
                                                'slug': ('%06x' % random.randrange(16**6)) })
                        if created:
                            if Song.objects.filter(slug=song_slug).exists():
                                song_slug += '-' + str(song_model.id)
                            song_model.slug = song_slug

                        else:
                            self.stdout.write("-> Already exists.")

                        artist_model.save()
                        song_model.save()

                    except IOError as e:
                        self.stderr.write("*** Failed processing file : "
                                          + filepath)
                        self.stderr.write("    I/O error({0}): {1}"
                                          .format(e.errno, e.strerror))
