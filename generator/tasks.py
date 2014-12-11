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


from background_task import background
from generator.models import Task as GeneratorTask
from generator.build import generate_songbook, GeneratorError

import datetime
import logging

LOGGER = logging.getLogger(__name__)

@background(schedule=datetime.datetime.now())
def queue_render_task(task_id):

    task = GeneratorTask.objects.get(id=task_id)
    task.state = GeneratorTask.State.IN_PROCESS
    task.save()

    try:
        filename = generate_songbook(task.songbook, task.layout)
    except GeneratorError as e:
        task.state = GeneratorTask.State.ERROR
        task.save()
        LOGGER.error("Failed task {0} (state : {1}): {2}"\
                      .format(task.id, task.state, e))

        return

    task.state = GeneratorTask.State.FINISHED
    task.result = {"file": "{0}".format(filename)}
    task.save()

    LOGGER.info("Finished task {0} (state : {1}) with result {2}"\
                 .format(task.id, task.state, task.result))
