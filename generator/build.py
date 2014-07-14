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

from generator.models import Songbook, Layout, Task
from django.conf import settings

from patacrep.build import SongbookBuilder
from patacrep.errors import SongbookError

import os
import hashlib


SONGBOOKS_PDFS = os.path.join(settings.MEDIA_ROOT, "PDF")


def _get_layout():
    """Default layout for PDF generation"""
    try:
        layout = Layout.objects.get(id=1)
    except Layout.DoesNotExist:
        layout = Layout.objects.create(bookoptions=["diagram", "pictures"])
    return layout


class GeneratorError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "[PDF Generator error] {0}". format(self.message)


def generate_songbook(songbook, layout):
    """Generate a PDF file by combining a songbook and a layout"""

    content = {}
    content.update(songbook.get_as_json())
    content.update(layout.get_as_json())

    content["datadir"] = settings.SONGS_LIBRARY_DIR

    tmpfile = str(songbook.id) + '-' + str(layout.id) + '-' + \
              hashlib.sha1(str(content)).hexdigest()[0:20]

    try:
        os.chdir(SONGBOOKS_PDFS)
    except OSError:
        os.makedirs(SONGBOOKS_PDFS)
        os.chdir(SONGBOOKS_PDFS)

    builder = SongbookBuilder(content, tmpfile)

    for step in ["tex", "pdf", "sbx", "pdf", "clean"]:
        try:
            builder.build_steps([step])
        except SongbookError:
            raise GeneratorError("Error during the step '{0}'".format(step))

    return tmpfile + ".pdf"
