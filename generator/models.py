# -*- coding: utf-8 -*-
#    Copyright (C) 2014 The Patacrep Team
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


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
import re


class Artist(models.Model):

    name = models.CharField(max_length=100, verbose_name=_(u'Nom'))
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
    user = models.ForeignKey(User, related_name='songbooks')
    author = models.CharField(max_length=255,
                              verbose_name=_(u"auteur"),
                              default="")

    def __unicode__(self):
        return self.title

    def hash(self):
        return hashlib.sha1(str(self.get_as_json()).encode()).hexdigest()

    def count_songs(self):
        count = ItemsInSongbook.objects.filter(
                   songbook=self,
                   item_type=ContentType.objects.get_for_model(Song)
                   ).count()
        return count

    def count_artists(self):
        songs = ItemsInSongbook.objects.prefetch_related(
                   'item'
                   ).filter(
                   songbook=self,
                   item_type=ContentType.objects.get_for_model(Song)
                   )
        artists = set()
        for song in songs:
            artists.add(song.item.artist_id)
        return len(artists)

    def count_section(self):
        count = ItemsInSongbook.objects.filter(
                   songbook=self,
                   item_type=ContentType.objects.get_for_model(Section)
                   ).count()
        return count

    def count_items(self):
        count = ItemsInSongbook.objects.filter(songbook=self).count()
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
             "author": self.author,
             "content": [],
             "authwords": {
               "sep": ["and", "et"]
             }
             }

        #Let the newlines of the description be compiled in Latex
        d["subtitle"] = re.sub(r'(\r\n|\r|\n)', "%\r\n\\\\newline%\r\n", d["subtitle"])

        items = ItemsInSongbook.objects.filter(songbook=self
                      ).order_by("rank").values_list("item_id", "item_type")
        item_ids = [i[0] for i in items]
        item_types = dict(items)

        types = { item_type:item.id for item_type, item in \
                 ContentType.objects.get_for_models(Song, Section).items()}

        song_ids = [i[0] for i in items if i[1] == types[Song]]
        song_paths = dict(Song.objects.filter(id__in=item_ids) \
                            .values_list("id", "file_path"))

        section_ids = [i[0] for i in items if i[1] == types[Section]]
        sections = dict(Section.objects.filter(id__in=item_ids) \
                            .values_list("id", "name"))

        for item_id in item_ids:
            if item_types[item_id] == types[Song]:
                d["content"].append(str(song_paths[item_id]))
            elif item_types[item_id] == types[Section]:
                d["content"].append(["songsection", sections[item_id]])

        return d

    def finished_tasks(self):
        return self.tasks.filter(
                   state='FINISHED'
                   )

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
              ("lyric", _(u"Sans accords")),
              )

    name = models.CharField(max_length=100,
                            verbose_name=_(u"nom de la mise en page"))

    booktype = models.CharField(max_length=10,
                                 choices=BOOKTYPES,
                                 default="chorded",
                                 verbose_name=_(u"type de carnet"))

    bookoptions = JSONField()
    other_options = JSONField()

    template = models.CharField(max_length=100,
                                 verbose_name=_(u"gabarit"),
                                 default="data.tex")

    def get_as_json(self):
        """Return a JSON representation of the layout"""
        layout = {}
        layout["booktype"] = self.booktype
        layout["bookoptions"] = self.bookoptions
        layout["template"] = self.template
        layout.update(self.other_options)
        return layout

    class Meta:
        verbose_name = _(u"Mise en page")


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
        unique_together = ('item_id', 'songbook',)


class Task(models.Model):
    """Model holding information for asynchronous PDF generation"""

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
    songbook = models.ForeignKey(Songbook,
                                 related_name="tasks",
                                 verbose_name=_(u"carnet"))
    layout = models.ForeignKey(Layout,
                               verbose_name=_(u"Mise en page"))
    hash = models.CharField(max_length=40,
                            verbose_name=_(u"contenu"))
    last_updated = models.DateTimeField(auto_now=True,
                                       verbose_name=_(u"dernière mise à jour"))
    state = models.CharField(max_length=20,
                             choices=STATES,
                             verbose_name=_(u"état"))
    result = JSONField(verbose_name=_(u"résultat"))

    def __unicode__(self):
        return _(u"Carnet '{songbook}', mise en page n°{layout}".format(
                                    songbook=self.songbook.title,
                                    layout=self.layout.id))
