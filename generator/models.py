# -*- coding: utf-8 -*-
import os
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
#from django.template.defaultfilters import slugify
from django.conf.global_settings import LANGUAGES
from django.utils.translation import ugettext_lazy as _

from jsonfield import JSONField
from numpy import rank
from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save


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

CHRD='chrd'
LYR='lyr'
BOOKTYPES=((CHRD,_("avec accords")),
           (LYR,_("sans accords"))
           )

class Songbook(models.Model):
    title = models.CharField(max_length=100, verbose_name=_("titre"))
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True, verbose_name=_("description"))
    is_public = models.BooleanField(default=False, verbose_name=_("carnet public"))
    bookoptions = JSONField()
    booktype = models.CharField(max_length=4,
                                choices=BOOKTYPES,
                                default=CHRD,
                                verbose_name=_("type de carnet"))
    template = models.CharField(max_length=100,
                                verbose_name=_("gabarit"),
                                default="patacrep.tmpl")
    #songbook['lang']='lang'
    #other_options = SerializedDataField()
    # Other options are : web mail picture picturecopyright footer license (a .tex file) 
    # mainfontsize songnumberbgcolor notebgcolor indexbgcolor 
    items = models.ManyToManyField(ContentType,
                                   blank=True,
                                   through='ItemsInSongbook',)
    user = models.ForeignKey('Profile', related_name='songbooks')
    
    def __unicode__(self):
        return self.title
    
    def count_songs(self):
        count = ItemsInSongbook.objects.filter(songbook=self,
                                               item_type__model="song").count()
        return count

    def count_section(self):
        count = ItemsInSongbook.objects.filter(songbook=self,
                                               item_type__model="section").count()
        return count

    def fill_holes(self):
        """fill the holes in the rank after deletion
        If their is two equal ranks, items are randomly sorted !
        """
        rank = 1
        item_list = ItemsInSongbook.objects.filter(songbook=self) 
        for item in item_list:
            item.rank = rank
            item.save()
            rank+=1

    class Meta:
        verbose_name = _("carnet de chants")
        verbose_name_plural = _("carnets de chants")


class Section(models.Model):
    name = models.CharField(max_length=200, 
                            verbose_name=_("nom de section"),)
    
    def __unicode__(self):
        return self.name


class ItemsInSongbook(models.Model):
    """Items in the songbooks model
    Every kind of item can be add : section, songs, images, etc.
    """
    item_type = models.ForeignKey(ContentType)
    item_id = models.PositiveIntegerField()
    item = generic.GenericForeignKey('item_type', 'item_id')
    songbook = models.ForeignKey(Songbook)
    rank = models.IntegerField(_("position"))
    
    def __unicode__(self):
        return _('{item_type} : "{item}", dans le carnet {songbook}' \
                 ).format(item=self.item, item_type =self.item_type, songbook=self.songbook)
     
    class Meta:
        ordering = ["rank"]

###############################################################

class Profile(models.Model):
    user = models.OneToOneField(User)

    def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name = _('profil')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user = instance)

class GitFile(models.Model):

    """Hold the information about the file object in a git repository.
    Attributes:
        file_path        string    path of the file in the songs repository
        commit_hash      string    hash of the commit the file was imported from
        object_hash      string    hash of the file object
    """

    # We use a CharField here, not FileField, we take care of the file.
    file_path = models.CharField(max_length=500)
    commit_hash = models.CharField(max_length=20)
    object_hash = models.CharField(max_length=20)

    def __unicode__(self):
        return "{0}:{1}".format(self.file_version, self.file_path)
