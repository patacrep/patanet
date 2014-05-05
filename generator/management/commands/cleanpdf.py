# Copyright (c) 2014 The songbook Team
#
# This program is distributed under the terms of the GNU General
# Public License as published by the Free Software Foundation;
# either version 2 of the License, or any later version.
# For more information, see the file LICENCE.txt

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

DELETE = settings.SONGBOOK_DELETE_POLICY

from generator.build import SONGBOOKS_PDFS
from generator.models import Task, Profile

from datetime import timedelta, datetime, tzinfo
import os


class UTC(tzinfo):
    """UTC timezone

    The choice of a time zone is not important, the timedelta is
    aware of the difference.
    """
    ZERO = timedelta(0)

    def utcoffset(self, dt):
        return self.ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return self.ZERO

# Settings
try:
    MODE = DELETE["mode"]
except:
    raise ImproperlyConfigured("PDF delete mode not found")

MAX_TIME = DELETE.get("expiration_time", timedelta.max)
MAX_NUMBER = int(DELETE.get("number", 0))


def _delete(task):
    os.unlink(os.path.join(SONGBOOKS_PDFS, task.result["file"]))
    task.delete()


def _time_delete():
    tasks = Task.objects.all()
    timezone = UTC()
    for task in tasks:
        if (datetime.now(timezone) - task.last_updated) > MAX_TIME:
            _delete(task)


def _number_delete():
    # tasks = Task.objects.all()
    users = Profile.objects.all()
    for user in users:
        try:
            tasks = Task.objects.filter(songbook__user=user
                                        ).order_by('last_updated')[0:MAX_NUMBER - 1]
            for task in tasks:
                _delete(task)
        except IndexError:
            pass
        except AssertionError:
            raise CommandError("Number based deletion and no max number giver")


def _tot_number_delete():
    try:
        tasks = Task.objects.order_by('last_updated')[0:MAX_NUMBER - 1]
        for task in tasks:
            _delete(task)
    except IndexError:
        pass
    except AssertionError:
            raise CommandError("Number based deletion and no max number giver")


class Command(BaseCommand):
    args = ""
    help = "Clean the PDF files according to the settings"

    def handle(self, *args, **options):
        os.chdir(SONGBOOKS_PDFS)
        if MODE == "time":
            _time_delete()
        elif MODE == "number":
            _number_delete()
        elif MODE == "total_number":
            _tot_number_delete()
        else:
            raise ImproperlyConfigured("Unknown deleting mode.")
