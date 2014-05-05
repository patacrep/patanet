# -*- coding: utf-8 -*-
# Copyright (c) 2014 The songbook Team
#
# This program is distributed under the terms of the GNU General
# Public License as published by the Free Software Foundation;
# either version 2 of the License, or any later version.
# For more information, see the file LICENCE.txt

from generator.models import Songbook, Layout
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


def generate_songbook(songbook, asked_layout=_get_layout()):
    if isinstance(songbook, Songbook):
        book = songbook
    else:
        try:
            book = Songbook.objects.get(id=int(songbook))
        except:
            raise GeneratorError("Songbook {0} not found.".format(songbook))

    content = book.get_as_json()

    if isinstance(asked_layout, Layout):
        layout = asked_layout
    else:
        try:
            layout = Layout.objects.get(id=int(asked_layout))
        except:
            raise GeneratorError("Layout {0} not found.".format(layout))

    content.update(layout.get_as_json())

    content["datadir"] = settings.SONGS_LIBRARY_DIR

    tmpfile = "songbook-{0}".format(book.id)

    if not os.path.exists(SONGBOOKS_PDFS):
        os.mkdir(SONGBOOKS_PDFS)
    os.chdir(SONGBOOKS_PDFS)

    builder = SongbookBuilder(content, tmpfile)

    for step in ["tex", "pdf", "sbx", "pdf", "clean"]:
        try:
            builder.build_steps([step])
        except SongbookError:
            raise GeneratorError("Error during the step '{0}'".format(step))

    return tmpfile + ".pdf"
