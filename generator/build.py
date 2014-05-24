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

from generator.models import Songbook, Layout, Task
from django.conf import settings

from songbook_core.build import SongbookBuilder
from songbook_core.errors import SongbookError

import os


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


def generate_songbook(task):
    
    book = task.songbook
    content = task.get_as_json()
    layout = task.layout

    content.update(layout.get_as_json())

    content["datadir"] = settings.SONGS_LIBRARY_DIR

    tmpfile = "songbook-{0}-{1}".format(book.id, layout.id)

    if not os.path.exists(SONGBOOKS_PDFS):
        os.mkdir(SONGBOOKS_PDFS)
    os.chdir(SONGBOOKS_PDFS)

    import pprint
    with open('/tmp/sb.log', 'w') as f:
        f.write(pprint.pformat(content))
    
    builder = SongbookBuilder(content, tmpfile)

    for step in ["tex", "pdf", "sbx", "pdf"]:
        try:
            builder.build_steps([step])
        except SongbookError:
            raise GeneratorError("Error during the step '{0}'".format(step))

    return tmpfile + ".pdf"
