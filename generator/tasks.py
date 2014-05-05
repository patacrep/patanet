# Copyright (c) 2014 The songbook Team
#
# This program is distributed under the terms of the GNU General
# Public License as published by the Free Software Foundation;
# either version 2 of the License, or any later version.
# For more information, see the file LICENCE.txt


from background_task import background
from generator.models import Songbook, Layout, \
                            Task as GeneratorTask
from generator.build import generate_songbook, GeneratorError

import datetime


@background(schedule=datetime.datetime.now())
def queue_render_task(songbook_id, layout_id):
    gt = GeneratorTask.objects.get(songbook__id=songbook_id,
                                   layout__id=layout_id)
    gt.state = GeneratorTask.State.IN_PROCESS
    gt.save()

    songbook = Songbook.objects.get(id=songbook_id)

    try:
        # Here we will add the layout id
        file = generate_songbook(songbook)
    except GeneratorError:
        gt.state = GeneratorTask.State.ERROR
        gt.save()

    gt.state = GeneratorTask.State.FINISHED
    gt.result = {"file": "{0}".format(file)}
    gt.save()

    # TODO: write this in a log file
    print("Finished task {0} (state : {1}) with result {2}"\
          .format(gt.id, gt.state, gt.result))
