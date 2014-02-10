from django.core.management.base import BaseCommand
from django.conf import settings
import sys
sys.path.append(settings.SONG_PROCESSOR_DIR)
from utils.plastex import parsetex
import pprint
import git
import os
from generator import models
from django.db import transaction
from django.utils.text import slugify
from django.utils.encoding import smart_text
from django.conf.global_settings import LANGUAGES

def _file_error(error):
    print(error)


class Command(BaseCommand):
    args = ""
    help = "Import song information into db"

    def handle(self, *args, **options):

        repo = git.Repo(settings.SONGS_LIBRARY_DIR)
        gitcmd = repo.git

        for root, dirs, filenames in os.walk(settings.SONGS_LIBRARY_DIR,
                                             topdown=True,
                                             onerror=_file_error,
                                             followlinks=False):

            for filename in filenames:
                if filename.lower().endswith(".sg"):
                    filepath = os.path.realpath(os.path.join(root, filename))
                    filepath_rel = os.path.relpath(filepath, settings.SONGS_LIBRARY_DIR)
                    try:
                        data = parsetex(filepath)
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
                                language_code = next((x for x in LANGUAGES if x[1].lower() == language_name.lower()), ('',''))[0]
                                if language_code == '':
                                    self.stderr.write("*** No code found for language : '" + language_name + "'")

                            song_title = smart_text(data['titles'][0], 'utf-8')
                            song_slug = slugify(song_title)
                            song_model, created = models.Song.objects.get_or_create(slug=song_slug,
                                                                                    defaults={'title':song_title,
                                                                                              'language':language_code,
                                                                                              'artist':artist_model})
                            if created:
                                self.stdout.write("-> Created.")
                            else:
                                self.stdout.write("-> Already exists.")
                                if (song_model.title != song_title):
                                    self.stderr.write("*** Song names differs though slugs are equal : "
                                                      + song_title + " / " 
                                                      + song_model.title)

                            gitfile = models.GitFile()

                            gitfile.object_hash = gitcmd.hash_object(filepath)

                            gitfile.commit_hash = gitcmd.log("-1",
                                                          "--pretty=format:%H",
                                                          "--", filepath)
                            gitfile.file_path = filepath_rel

                            song_model.file = gitfile

                            artist_model.save()
                            gitfile.save()
                            song_model.save()

                    except IOError as e:
                        self.stderr.write("*** Failed processing file : " + filepath)
                        self.stderr.write("    I/O error({0}): {1}".format(e.errno, e.strerror))
