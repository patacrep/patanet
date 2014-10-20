Patanet
============

Web interface for songbook generation, as part of the [patacrep](http://www.patacrep.com/fr/index.php) project.

Build with Django 1.7, only suport python 2.7 for now, should be quickly updated to Python >= 3.3.

## Installation

### Short version

Install libgit2 [from sources](https://libgit2.github.com/docs/guides/build-and-link/), or with your favorite package manager :
```
apt-get install libgit2-21 libgit2-dev # https://packages.debian.org/jessie/libgit2-21
brew install libgit2
yum install libgit2
```

Install the project
```
[virtualenv|pyvenv] virtualacrep
source virtualacrep/bin/activate
git clone https://github.com/patacrep/patanet
git clone https://github.com/patacrep/patadata
cd patanet
pip install -r Requirements.txt
pip install patacrep=4.0.0alpha
cp patanet/local_settings.sample.py patanet/local_settings.py
<edit> patanet/local_settings.py
./manage.py migrate
./manage.py createsuperuser
./manage.py importsongs
```

Don't forget about `patacrep` dependencies: pdflatex and [lilypond](http://www.lilypond.org/).

### Long version

Create a virtualenv to isolate the code from your system (virtualenv for Python 2.7, pyvenv for Python 3)
```
[virtualenv|pyvenv] virtualacrep
source virtualacrep/bin/activate
```

Get the source
```
git clone https://github.com/patacrep/patanet
```
Get a song database
```
git clone https://github.com/patacrep/patadata
```

Install the Python dependencies
```
cd patanet
pip install -r Requirements.txt
pip install patacrep=4.0.0alpha
```

Go to the patanet folder and configure the local settings
```
cp patanet/local_settings.sample.py patanet/local_settings.py
<edit> patanet/local_settings.py
```

Update and fill the database
```
./manage.py migrate
./manage.py createsuperuser
./manage.py importsongs
```

Again, don't forget about `patacrep` dependencies: pdflatex and [lilypond](http://www.lilypond.org/).


## Run
You can start a development server with `./manage.py runserver`. Then access to the website at `http://localhost:8000` URI.

Start a background songbook compiler with `./manage.py process_tasks`.

There is a Wiki page about how to [deploye the app](https://github.com/patacrep/patanet/wiki/Deploying-the-app) in production.


## Join the team

If you want to help, we need various competencies:

* Front-end dev, with HTML/CSS/JS abilities
* Back-end dev, with Python/Django abilities
