# Copyright (c) 2014 The songbook Team
#
# This program is distributed under the terms of the GNU General
# Public License as published by the Free Software Foundation;
# either version 2 of the License, or any later version.
# For more information, see the file LICENCE.txt


from background_task import background
from django.conf import settings
from songbook_core.build import SongbookBuilder
from songbook_core.errors import SongbookError
from generator.models import Songbook, SongbookLayout, \
                            Task as GeneratorTask
import datetime
import os

SONGBOOKS_PDFS = os.path.join(settings.MEDIA_ROOT,
                              "PDF")


@background(schedule=datetime.datetime.now())
def queue_render_task(songbook_id):

    gt = GeneratorTask.objects.get(songbook__id=songbook_id)
    gt.state = GeneratorTask.State.IN_PROCESS
    gt.save()

    book = Songbook.objects.get(id=songbook_id)
    content = book.get_as_json()

    layout = SongbookLayout()
    content.update(layout.get_as_json())

    content["datadir"] = settings.SONGS_LIBRARY_DIR

    tmpfile = "songbook-{0}".format(songbook_id)

    import os
    if not os.path.exists(SONGBOOKS_PDFS):
        os.mkdir(SONGBOOKS_PDFS)
    os.chdir(SONGBOOKS_PDFS)

    builder = SongbookBuilder(content, tmpfile)

    try:
        builder.build_steps(["tex", "pdf", "sbx", "pdf"])
    except SongbookError:
        gt.state = GeneratorTask.State.ERROR
        gt.save()

    # TODO: meilleur gestion des erreurs.
    try:
        builder.build_steps(["clean"])
    except:
        pass

    gt.state = GeneratorTask.State.FINISHED
    gt.result = {"file": "{0}.pdf".format(tmpfile)}
    gt.save()

    # TODO: write this in a log file
    print("Finished task {0} (state : {1}) with result {2}"\
          .format(gt.id, gt.state, gt.result))
