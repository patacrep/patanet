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

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction

from generator.management.songs import import_song

import os

SONGS_DIR = os.path.join(settings.SONGS_LIBRARY_DIR, "songs")

@transaction.atomic
class Command(BaseCommand):
    args = ""
    help = "Import song information into db"

    def handle(self, *args, **options):
        for root, _dirs, filenames in os.walk(SONGS_DIR,
                                             topdown=True,
                                             onerror=_file_error,
                                             followlinks=False):
            for filename in filenames:
                if filename.lower().endswith(".sg"):
                    filepath = os.path.realpath(os.path.join(root, filename))
                    try:
                        import_song(filepath, SONGS_DIR)
                    except IOError as e:
                        self.stderr.write("*** Failed processing file : "
                                          + filepath)
                        self.stderr.write("    I/O error({0}): {1}"
                                          .format(e.errno, e.strerror))

def _file_error(error):
    print(error)
