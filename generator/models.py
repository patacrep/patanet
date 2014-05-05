# -*- coding: utf-8 -*-
# Copyright (c) 2014 The songbook Team
#
# This program is distributed under the terms of the GNU General
# Public License as published by the Free Software Foundation;
# either version 2 of the License, or any later version.
# For more information, see the file LICENCE.txt


from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.conf.global_settings import LANGUAGES
from django.utils.translation import ugettext_lazy as _
from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save

from jsonfield import JSONField
import hashlib


class Artist(models.Model):

    name = models.CharField(max_length=100, verbose_name='Nom')
    slug = models.SlugField(max_length=100, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u"artiste")
        ordering = ["name"]


class Song(models.Model):
    title = models.CharField(max_length=100, verbose_name=_(u'titre'))
    slug = models.SlugField(max_length=100, unique=True)
    # Pick the language as e.g. fr-FR or sr-latn from the list
    # provided by django
    language = models.CharField(max_length=7, choices=LANGUAGES, null=True)
    capo = models.IntegerField(null=True, blank=True)
    artist = models.ForeignKey(Artist,
                               verbose_name=_(u'artiste'),
                               related_name="songs")
    file_path = models.CharField(max_length=500)
    object_hash = models.CharField(max_length=50)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _(u"chant")
        ordering = ["title"]

###############################################################


class Songbook(models.Model):
    title = models.CharField(max_length=100,
                             verbose_name=_(u"titre")
                             )
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True,
                                   verbose_name=_(u"description")
                                   )
    is_public = models.BooleanField(default=False,
                                    verbose_name=_(u"carnet public")
                                    )
    items = models.ManyToManyField(ContentType,
                                   blank=True,
                                   through='ItemsInSongbook',)
    user = models.ForeignKey('Profile', related_name='songbooks')

    def __unicode__(self):
        return self.title

    def hash(self):
        return hashlib.sha1(str(self.get_as_json())).hexdigest()

    def count_songs(self):
        count = ItemsInSongbook.objects.filter(
                   songbook=self,
                   item_type=ContentType.objects.get_for_model(Song)
                   ).count()
        return count

    def count_section(self):
        count = ItemsInSongbook.objects.filter(
                   songbook=self,
                   item_type=ContentType.objects.get_for_model(Section)
                   ).count()
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
            rank += 1

    def add_section(self, name):
        section = Section.objects.create(name=name)
        section.save()

        rank = ItemsInSongbook.objects.filter(songbook=self).count() + 1

        ItemsInSongbook.objects.create(songbook=self, item=section, rank=rank)

    def get_as_json(self):

        d = {"subtitle": self.description,
             "title": self.title,
             "version": "0.1",
             "author": self.user.user.username,
             "content": [],
             "authwords": {
               "sep": ["and", "et"]
             }
             }
        item_ids = ItemsInSongbook.objects.filter(
                      songbook=self,
                      item_type=ContentType.objects.get_for_model(Song)
                      ).order_by("rank").values_list("item_id", flat=True)

        song_paths = Song.objects.filter(id__in=item_ids) \
                            .values_list("file_path", flat=True)

        for song_path in song_paths:
            d["content"].append(str(song_path))

        return d

    class Meta:
        verbose_name = _(u"carnet de chants")
        verbose_name_plural = _(u"carnets de chants")


class Section(models.Model):
    name = models.CharField(max_length=200,
                            verbose_name=_(u"nom de section"),
                            )

    def __unicode__(self):
        return self.name


class Layout(models.Model):
    """
    This class holds layout information for generating a songbook.
    """
    BOOKTYPES = (("chorded", _(u"Avec accords")),
              ("lyrics", _(u"Sans accords")),
              )

    bookoptions = JSONField()
    booktype = models.CharField(max_length=4,
                                 choices=BOOKTYPES,
                                 default="chorded",
                                 verbose_name=_("type de carnet"))
    template = models.CharField(max_length=100,
                                 verbose_name=_("gabarit"),
                                 default="patacrep.tex")
    lang = models.CharField(max_length=10,
                                verbose_name=_("langue principale"),
                                default="french")
    other_options = JSONField(default=[])

#     Other options are : web mail picture picturecopyright footer
#     license (a .tex file) mainfontsize songnumberbgcolor notebgcolor
#     indexbgcolor

    def get_as_json(self):
        """Return a JSON representation of the layout"""
        layout = {"template": self.template,
                  "lang": self.lang,
                  "bookoptions": self.bookoptions,
                  "booktype": self.booktype,
                  }
        layout.update(self.other_options)
        return layout

    class Meta:
        verbose_name = _(u"Layout")


class ItemsInSongbook(models.Model):
    """Items in the songbooks model
    Every kind of item can be add : section, songs, images, etc.
    """
    item_type = models.ForeignKey(ContentType)
    item_id = models.PositiveIntegerField()
    item = generic.GenericForeignKey('item_type', 'item_id')
    songbook = models.ForeignKey(Songbook)
    rank = models.IntegerField(_(u"position"))

    def __unicode__(self):
        return _('"{item_type}" : "{item}", dans le carnet "{songbook}"'
                 ).format(item=self.item,
                          item_type=self.item_type,
                          songbook=self.songbook
                          )

    class Meta:
        ordering = ["rank"]


class Task(models.Model):
    """Model holding informations for asynchroneous PDF generation"""

    class State(object):
        QUEUED = "QUEUED"
        IN_PROCESS = "IN_PROCESS"
        FINISHED = "FINISHED"
        ERROR = "ERROR"

    STATES = ((State.QUEUED, "Queued"),
              (State.IN_PROCESS, "In process"),
              (State.FINISHED, "Finished"),
              (State.ERROR, "Error"),
              )
    songbook = models.ForeignKey(Songbook, related_name="tasks")
    layout = models.ForeignKey(Layout)
    hash = models.CharField(max_length=40,
                            verbose_name=_(u"contenu"))
    last_updated = models.DateTimeField(auto_now=True)
    state = models.CharField(max_length=20,
                             choices=STATES,
                             verbose_name=_(u"état"))
    result = JSONField(verbose_name=_(u"résultat"))

    def __unicode__(self):
        return _(u"Carnet '{songbook}', mise en page n°{layout}".format(
                                    songbook=self.songbook.title,
                                    layout=self.layout.id))

###############################################################


class Profile(models.Model):
    user = models.OneToOneField(User)

    def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name = _(u'profil')


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
