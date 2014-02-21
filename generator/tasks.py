from background_task import background
from django.conf import settings
import sys
sys.path.append(settings.SONG_PROCESSOR_DIR)
from songbook.build import buildsongbook
from generator.models import Songbook, SongbookLayout
import tempfile
import json
import datetime


@background(schedule=datetime.datetime.now())
def queue_render_task(songbook_id):

    book = Songbook.objects.get(id=songbook_id)
    content = book.get_as_json()

    layout = SongbookLayout()
    content.update(layout.get_as_json())

    content["datadir"] = settings.SONGS_LIBRARY_DIR

    sb_file = tempfile.NamedTemporaryFile(suffix=".sb", delete=False)
    json.dump(content, sb_file, indent=2)
    sb_file.close()

    # sb_file will be used for background task management.

    import os
    print os.path.basename(sb_file.name)

    buildsongbook(content, os.path.basename(sb_file.name))
