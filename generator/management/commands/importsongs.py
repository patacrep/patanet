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
from django.utils.encoding import smart_text

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

            for file in filenames:
                if file.lower().endswith(".sg"):
                    filename = os.path.join(root, file)
                    try:
                        data = parsetex(filename)
                        self.stdout.write("Processing " + pprint.pformat(data['titles'][0]))

                        artist_name = smart_text(data['args']['by'], 'utf-8')
                        artist_slug = slugify(artist_name)

                        with transaction.atomic():
                            artist_model, created = models.Artist.objects.get_or_create(slug=artist_slug,
                                                                                        defaults={'name':artist_name})
                            if not created:
                                if (artist_model.name != artist_name):
                                    self.stderr.write("*** Artist name differs though slugs are equal : "
                                                      + artist_name + " / " 
                                                      + artist_model.name)

                            if (len(data['languages']) > 1):
                                self.stderr.write("*** Multiple languages " +
                                                  "in song file; we though" +
                                                  " only support one. " +
                                                  "Picking any.")
                            if (len(data['languages']) > 0):
                                language_name = data["languages"].pop()
                                language_model, created = models.Language.objects.get_or_create(name=language_name,
                                                                                                defaults={'code':language_name[:6]})
                                # TODO: fill with country code

                            song_title = smart_text(data['titles'][0], 'utf-8')
                            song_slug = slugify(song_title)
                            song_model, created = models.Song.objects.get_or_create(slug=song_slug,
                                                                                    defaults={'title':song_title,
                                                                                              'language':language_model,
                                                                                              'artist':artist_model})
                            if not created:
                                if (song_model.title != song_title):
                                    self.stderr.write("*** Song names differs though slugs are equal : "
                                                      + song_title + " / " 
                                                      + song_model.title)

                            gitfile = models.GitFile()
                            gitfile.file_path = filename
                            gitfile.file_version = filerev

                            song_model.file = gitfile

                            artist_model.save()
                            language_model.save()
                            gitfile.save()
                            song_model.save()

                    except IOError as e:
                        self.stderr.write("*** Failed processing file : " + filename)
                        self.stderr.write("    I/O error({0}): {1}".format(e.errno, e.strerror))
