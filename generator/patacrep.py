# -*- coding: utf-8 -*-
#    Copyright (C) 2015 The Patacrep Team
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
Patacrep bridge
"""

from patacrep.build import SongbookBuilder
from patacrep.errors import SongbookError

def build_songbook(content, outputfile, steps):
    builder = SongbookBuilder(content, outputfile)
    for step in steps:
        try:
            builder.build_steps([step])
        except SongbookError as e:
            from generator.build import GeneratorError
            raise GeneratorError("Error during the step '{0}': {1}".format(step, e))
