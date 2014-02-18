from django.conf import settings
import sys
sys.path.append(settings.SONG_PROCESSOR_DIR)
from songbook.build import buildsongbook
from django.core.management.base import LabelCommand
from generator.models import Songbook, SongbookLayout
import tempfile
import json


class Command(LabelCommand):
    args = ""
    help = "Import song information into db"

    def handle_label(self, label, **options):

        book = Songbook.objects.get(slug=label)
        content = book.get_as_json()

        layout = SongbookLayout()
        content.update(layout.get_as_json())

        content["datadir"] = settings.SONGS_LIBRARY_DIR

        sb_file = tempfile.NamedTemporaryFile(suffix=".sb", delete=False)
        self.stdout.write("Wrote to " + sb_file.name)
        json.dump(content, sb_file, indent=2)
        sb_file.close()

        # sb_file will be used for background task management.

        import os
        print os.path.basename(sb_file.name)

        buildsongbook(content, os.path.basename(sb_file.name))
