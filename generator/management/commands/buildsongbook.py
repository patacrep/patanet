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

from django.core.management.base import BaseCommand, CommandError

from generator.build import generate_songbook, GeneratorError
from generator.models import Songbook, Layout


class Command(BaseCommand):
    args = "<songbook_id> <layout_id>"
    help = "Build the PDF corresponding to a songbook given a layout"

    def handle(self, songbook_id, layout_id, *args, **options):
        songbook = Songbook.objects.get(id=songbook_id)
        layout = Layout.objects.get(id=layout_id)
        try:
            generate_songbook(songbook, layout)
        except GeneratorError as e:
            raise CommandError(str(e))
