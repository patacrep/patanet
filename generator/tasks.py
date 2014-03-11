from background_task import background
from django.conf import settings
from songbook_core.build import buildsongbook
from generator.models import Songbook, SongbookLayout, \
                            Task as GeneratorTask
import datetime


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
    if not os.path.exists(settings.SONGBOOKS_PDFS):
        os.mkdir(settings.SONGBOOKS_PDFS)
    os.chdir(settings.SONGBOOKS_PDFS)

    buildsongbook(content, tmpfile)

    gt.state = GeneratorTask.State.FINISHED
    gt.result = {"file": "{0}.pdf".format(tmpfile)}
    gt.save()

    print("Finished task {0} (state : {1}) with result {2}"\
          .format(gt.id, gt.state, gt.result))
