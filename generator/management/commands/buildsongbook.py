# Copyright (c) 2014 The songbook Team
#
# This program is distributed under the terms of the GNU General
# Public License as published by the Free Software Foundation;
# either version 2 of the License, or any later version.
# For more information, see the file LICENCE.txt
from django.core.management.base import BaseCommand, CommandError

from generator.build import generate_songbook, GeneratorError


class Command(BaseCommand):
    args = "<songbook_id>"
    help = "Build the PDF corresponding to a songbook given an id"

    def handle(self, sb_id, *args, **options):
        try:
            generate_songbook(sb_id)
        except GeneratorError as e:
            raise CommandError(str(e))
