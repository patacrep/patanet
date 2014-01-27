songbook-web
============

Web interface for songbook generation (see https://github.com/crep4ever/songbook or http://www.patacrep.com/fr/index.php)

## Installation

Be sure you have Python and Django (1.6.1) installed.
You will also need the 'south' package (see http://south.readthedocs.org/en/latest/installation.html). 
In short : `pip install south` or `easy_install South`.

## Configuration

Init the DB with:
```
./manage.py syncdb
./manage.py migrate
```
If wished, you can load some test data:
```
./manage.py loaddata few_songs.json
```
Or, probably better, you can import songs from a songbook repository like that:

1. if not yet done, make a copy of `Songbook_web/local_settings.sample.py`to `Songbook_web/local_settings.py`
1. set some variables in `local_settings.py` :
 * Path to the root of the songbook repo: 
 `SONG_PROCESSOR_DIR = os.path.join(PROJECT_ROOT, '../songbook/')`
 * Path to the songs in the songbook repo: 
 `SONGS_LIBRARY_DIR = os.path.join(SONG_PROCESSOR_DIR, 'songs/')`

2. run `./manage.py importsongs`

## How to run

Then you can run a development server with the command `python manage.py runserver`. No web server (e.g. Apache, ...) required.

## This is a development version !

And it is not usable yet ! Lot of things just don't work. Check the wiki to know what's missing.

