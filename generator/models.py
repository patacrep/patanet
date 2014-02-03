# -*- coding: utf-8 -*-
import os
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.conf.global_settings import LANGUAGES

from jsonfield import JSONField


class Artist(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nom')
    # FIXME: cas de deux artistes de même slug
    slug = models.SlugField(max_length=100, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _("artiste")
        ordering = ["name"]


class Song(models.Model):
    title = models.CharField(max_length=100, verbose_name=_('titre'))
    slug = models.SlugField(max_length=100, unique=True)
    artist = models.ForeignKey(Artist, verbose_name=_('artiste'),related_name="songs")
    # Pick the language as e.g. fr-FR or sr-latn from the list
    # provided by django
    language = models.CharField(max_length=7, choices=LANGUAGES, null=True)
    capo = models.IntegerField(null=True, blank=True)
    file = models.OneToOneField('GitFile', null=True)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _("chant")
        ordering = ["title"]

###############################################################


# def get_songbook_path(songbook, filename):
#     user_directory = slugify(songbook.user.username)
#     filename = slugify(songbook.title) + ".sb"
#     return os.path.join(user_directory, filename)

CHRD='chrd'
LYR='lyr'
BOOKTYPES=((CHRD,_("Avec accords")),
           (LYR,_("Sans accords"))
           )

class Songbook(models.Model):
    title = models.CharField(max_length=100, verbose_name=_("titre"))
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True, verbose_name=_("description"))
    is_public = models.BooleanField(default=False, verbose_name=_("carnet public"))
    bookoptions = JSONField()
    booktype = models.CharField(max_length=4, choices=BOOKTYPES, default=CHRD)
    template = models.CharField(max_length=100,
                                verbose_name=_("gabarit"),
                                default="patacrep.tmpl")
    #songbook['lang']='lang'
    #other_options = SerializedDataField()
    # Other options are : web mail picture picturecopyright footer license (a .tex file) 
    # mainfontsize songnumberbgcolor notebgcolor indexbgcolor 
    songs = models.ManyToManyField(Song,
                                   blank=True,
                                   through='SongsInSongbooks',
                                   related_name='songs')
                                   
    users = models.ManyToManyField('Profile',
                                       blank=True,
                                       through='SongbooksByUser',
                                       related_name='users')
    
    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _("carnet de chants")
        verbose_name_plural = _("carnets de chants")


class SectionInSongbooks(models.Model):
    name = models.CharField(max_length=200, 
                            verbose_name=_("nom de section"),
                            default="main section"
                            )
    
    def __unicode__(self):
        return self.name
    

class SongsInSongbooks(models.Model):
    """Songs in songbooks model
    Every song has a rank in the section, and a section ("main section" as default)
    """
    song = models.ForeignKey(Song)
    songbook = models.ForeignKey(Songbook)
    section = models.ForeignKey(SectionInSongbooks,blank=False, related_name='section')
    rank_in_section = models.IntegerField(_("position"))
    
    def __unicode__(self):
        return _("Chant {song}, dans le carnet {songbook}" \
                 ).format(song=self.song, songbook=self.songbook)
    class Meta:
        unique_together = ('section','rank_in_section')

###############################################################

class Profile(models.Model):
    user = models.OneToOneField(User)
    songbooks = models.ManyToManyField(Songbook,
                                       blank=True,
                                       through='SongbooksByUser',
                                       related_name='songbooks')

    def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name = _('profil')


class SongbooksByUser(models.Model):
    is_owner = models.BooleanField(default=False)
    user = models.ForeignKey('Profile')
    songbook = models.ForeignKey('Songbook')

    def __unicode__(self):
        return _("Carnet de chant {songbook_name}, utilisé par {user}" \
                 ).format(songbook_name=self.songbook, user=self.user)


class GitFile(models.Model):

    """Hold the information about the file object in a git repository.
    Attributes:
        file_path        string    path of the file in the songs repository
        file_version     string    version of the file as currently known in db
    """

    # We use a CharField here, not FileField, we take care of the file.
    file_path = models.CharField(max_length=500)
    file_version = models.CharField(max_length=20)

    def __unicode__(self):
        return "{0}:{1}".format(self.file_version, self.file_path)
