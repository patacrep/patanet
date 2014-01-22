from django.core.management.base import BaseCommand
from django.conf import settings
import sys
sys.path.append(settings.SONG_PROCESSOR_DIR)
from utils.plastex import parsetex
import pprint
import sh
import os
from generator import models
from django.db import transaction
from django.utils.text import slugify


def _file_error(error):
    print(error)


class Command(BaseCommand):
    args = ""
    help = "Import song information into db"

    def handle(self, *args, **options):

        git = sh.git.bake(_cwd=settings.SONGS_LIBRARY_DIR)
        filerev = git("rev-parse", "HEAD")

        for root, dirs, filenames in os.walk(settings.SONGS_LIBRARY_DIR,
                                             topdown=True,
                                             onerror=_file_error,
                                             followlinks=False):
            for f in filenames:
                self.stdout.write("- {0}".format(os.path.join(root, f)))
                if f.lower().endswith(".sg"):
                    filename = os.path.join(root, f)
                    try:
                        data = parsetex(filename)
                        self.stdout.write(pprint.pformat(data))
                        self.stdout.write(pprint.pformat(data['titles'][0]))

                        with transaction.atomic():

                            song_title = data['titles'][0]
                            song_slug = slugify(unicode(song_title))
                            song_model, created = models.Song.objects.get_or_create(slug=song_slug)
                            if created:
                                song_model.title = song_title


                            if (len(data['languages']) > 1):
                                self.stderr.write("*** Multiple languages " +
                                                  "in song file; we though" +
                                                  " only support one. " +
                                                  "Picking any.")
                            if (len(data['languages']) > 0):
                                language_name = data["languages"].pop()
                                self.stdout.write(pprint.pformat(language_name))
                                language_model, created = models.Language.objects.get_or_create(name=language_name)
                                if (created is True):
                                    # TODO: fill with country code
                                    language_model.code = language_name[:6]
                                    language_model.save()

                            artist_name = data['args']['by']
                            artist_slug = slugify(unicode(artist_name))

                            artist_model, created = models.Artist.objects.get_or_create(slug=artist_slug)
                            if (created is True):
                                artist_model.name = artist_name
                            else:
                                if (artist_model.name != artist_name):
                                    self.stderr.write("*** Artist name differs though slugs are equal : "
                                                      + artist_name + " / " + artist_model.name)

                            song_model.language = language_model
                            song_model.artist = artist_model

                            gitfile = models.GitFile()
                            gitfile.file_path = f
                            gitfile.file_version = filerev

                            song_model.file = gitfile

                            artist_model.save()
                            language_model.save()
                            gitfile.save()
                            song_model.save()

                    except IOError as e:
                        self.stderr.write("*** Failed processing file : " + filename)
                        self.stderr.write("    I/O error({0}): {1}".format(e.errno, e.strerror))
