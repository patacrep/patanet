from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import sys
sys.path.append(settings.SONG_PROCESSOR_DIR)
from utils.plastex import parsetex
import pprint
import sh
import os
from generator import models

def _file_error(error):
    print(error)

class Command(BaseCommand):
    args = ""
    help = "Import song information into db"


    def handle(self, *args, **options):

        
#        try:
        git = sh.git.bake(_cwd=settings.SONGS_LIBRARY_DIR)
        filerev = git("rev-parse", "HEAD")
        
        for root, dirs, filenames in os.walk(settings.SONGS_LIBRARY_DIR, topdown=True, onerror=_file_error, followlinks=False):
            for f in filenames:
                self.stdout.write("- {0}".format(os.path.join(root, f)))
                if f.lower().endswith(".sg"):
                    filename = os.path.join(root, f)
                    try:
                        data = parsetex(filename)
                        self.stdout.write(pprint.pformat(data))
                        self.stdout.write(pprint.pformat(data['titles'][0]))

                        song = models.Song();
                        song.title = data['titles'][0]
                        
                        if (len(data['languages']) > 1):
                            self.stderr.write("*** Multiple languages in song file; we though only support one. Picking any.")
                        if (len(data['languages']) > 0):
                            language_name = data["languages"].pop()
                            self.stdout.write(pprint.pformat(language_name))
                            language_model = models.Language.objects.get(language_name)
                            if (language_model is None):
                                language_model = models.Language()
                                language_model.name = language_name
                                language_model.code = language_name[:6]
                                language_model.save()
                        
                        song.language = language_model
                        song.slug = django.utils.text.slugify(song.title)
                        song.save
                        
                        
                    except IOError as e:
                        self.stderr.write("*** Failed processing file : " + filename)
                        self.stderr.write("    I/O error({0}): {1}".format(e.errno, e.strerror))

#         except Exception as e:
#             self.stderr.write("*** Caught exception of type : " + str(type(e)))
#             self.stderr.write("    " + str(e.args))
