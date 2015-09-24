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


from patanet.settings import SONGS_LIBRARY_DIR, PROJECT_ROOT


from patacrep.build import DEFAULT_CONFIG
from patacrep.songs.chordpro import ChordproSong

from pathlib import PurePosixPath

import os

from django.conf import settings
from django.utils.safestring import mark_safe
from django.templatetags.static import static

class Chordpro2HtmlSong(ChordproSong):

    def __init__(self, filename):
        # TODO: Clean this hack
        # Hack to read the .sgc file
        filename += "c"

        relpath = os.path.join('songs', filename)

        datadir = os.path.abspath(settings.SONGS_LIBRARY_DIR)
        config = DEFAULT_CONFIG.copy()
        config['datadir'].append(datadir)
        super().__init__(datadir, relpath, config)

        self.more = {
            'failed': (self.titles == []),
        }

    def search_file(self, filename, extensions=None, directories=None):
        filepath = super().search_file(filename, extensions, directories)
        if not filepath:
            return None
        return static(PurePosixPath(filepath).relative_to(self.datadir).as_posix())

    def render_html(self):
        return super().render(
            "html",
            None,
            templatedirs=[os.path.join(settings.PROJECT_ROOT, 'templates', 'song')],
            )
