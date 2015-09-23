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
from functools import wraps

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

        # TODO Clean after this line
        def path_decorator(f):
            """Transform the filepath to an URL"""
            @wraps(f)
            def wrapper(*args, **kwds):
                filepath = f(*args, **kwds)
                if not filepath:
                    return None
                relpath = str(PurePosixPath(filepath).relative_to(datadir))
                return static(relpath)
            return wrapper
        self.search_file = path_decorator(self.search_file)

        self.more = {
            'failed': (self.titles == []),
        }

    def render_html(self):
        # TODO: Clean this file
        custom_template = os.path.join(settings.PROJECT_ROOT, 'templates', 'song')
        self.add_template_path(custom_template)
        return super().render(None, "html")


    def get_cover_url(self, datadir):
        if not self.cover_filepath:
            return None
        relfile = str(PurePosixPath(self.cover_filepath).relative_to(datadir))
        return relfile
