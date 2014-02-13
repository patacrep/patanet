# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Max
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.conf.global_settings import LANGUAGES
from django.utils.translation import ugettext_lazy as _

from jsonfield import JSONField
from django.db import transaction


class ArtistCommon(models.Model):

    name = models.CharField(max_length=100, verbose_name='Nom')
    # FIXME: cas de deux artistes de même slug
    slug = models.SlugField(max_length=100, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _("artiste")
        ordering = ["name"]
        abstract = True


class Artist(ArtistCommon):

    pass


class SongCommon(models.Model):
    title = models.CharField(max_length=100, verbose_name=_('titre'))
    slug = models.SlugField(max_length=100, unique=True)
    # Pick the language as e.g. fr-FR or sr-latn from the list
    # provided by django
    language = models.CharField(max_length=7, choices=LANGUAGES, null=True)
    capo = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.title

    class Meta:
        abstract = True
        ordering = ["title"]


class Song(SongCommon):

    artist = models.ForeignKey(Artist,
                               verbose_name=_('artiste'),
                               related_name="songs")
    file = models.OneToOneField('GitFile', null=True)

    class Meta:
        verbose_name = _("chant")

###############################################################

CHRD = 'chrd'
LYR = 'lyr'
BOOKTYPES = ((CHRD, _("Avec accords")),
           (LYR, _("Sans accords"))
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
    items = models.ManyToManyField(ContentType,
                                   blank=True,
                                   through='ItemsInSongbook',
                                   related_name='items')
    users = models.ManyToManyField('Profile',
                                       blank=True,
                                       through='SongbooksByUser',
                                       related_name='users')

    def __unicode__(self):
        return self.title

    def add(self, item, rank=-1):
        """Add an item to the songbook.
        
        Parameters:
        
            item :    the item to add
            rank :    position where to add the item. If an item is already
                      at this position, the latter will be shifted after 
                      the new one.
                      Use '-1' to add at the end (default)
        """
        
        if item is None:
            raise TypeError("item may not be None.")
        
        if type(item) is Song:
            return self.add_song(item)
            
        else:
            raise NotImplemented("Cannot handle adding objects of type {0}".format(type(item)))
            
    def add_song(self, song, rank=-1):
        """Add a song to this songbook. This creates a cache of the song
        and of the related information: artist and file.
        
        If the song is already in the book, nothing is done.
        
        Parameters:
        
            song :    the song to add
            rank :    position where to add the song. If an item is already
                      at this position, the latter will be shifted after 
                      the new one.
                      Use '-1' to add at the end (default)
        """
        
        if song is None:
            raise TypeError("song may not be None.")

        if type(song) is not Song:
            raise TypeError("Parameter song should be of type Song")

        if ItemsInSongbook.objects.filter(item_id=song.id, 
                                          item_type=ContentType.objects.get_for_model(Song),
                                          songbook=self
                                          ).count() > 0:
            return
        
        with transaction.atomic():

            artist = song.artist
            artist_in_sb = ArtistInSongbook.objects.get_or_create(artist=artist,
                                                                  defaults={'name': artist.name,
                                                                            'slug': artist.slug}
                                                                  )[0]

            songfile = song.file
            file_in_sb = FileInSongbook.objects.create(object_hash=songfile.object_hash,
                                                       commit_hash=songfile.commit_hash,
                                                       file_path=songfile.file_path)

            song_in_sb = SongInSongbook.objects.get_or_create(song=song,
                                                              defaults={'artist': artist_in_sb,
                                                                        'title': song.title,
                                                                        'slug': song.slug,
                                                                        'capo': song.capo,
                                                                        'language': song.language,
                                                                        'file': file_in_sb}
                                                              )[0]

            artist_in_sb.save()
            file_in_sb.save()
            song_in_sb.save()

            if rank == -1:
                rank = ItemsInSongbook.objects.filter(songbook=self).aggregate(Max("rank"))["rank__max"]
                if rank is None:  # possible if no item yet
                    rank = 0
            else:
                # FIXME: find a better algorithm to let the rank be just 
                # before an existing item.
                rank -= 0.0001
            
            iis = ItemsInSongbook(item=song_in_sb, songbook=self, rank=rank)
            iis.save()
            
        self.fill_holes()

    def remove_song(self, song_id):

        iis = ItemsInSongbook.objects.values_list('item_id', flat=True).filter(songbook=self,
                                             item_type=ContentType.objects.get_for_model(SongInSongbook))
        
        sis = SongInSongbook.objects.get(id__in=iis, song_id=song_id)
        
        if sis is not None:
            if sis.artist.songs_in_songbooks.count() == 1:
                # If this SongInSongbook is the last one for the ArtistInSongbook
                # so delete the ArtistInSongbook
                sis.artist.delete()
            
            sis.file.delete()

            item = ItemsInSongbook.objects.get(item_type=ContentType.objects.get_for_model(SongInSongbook),
                                               item_id=sis.id,
                                               songbook=self)
            
            if ItemsInSongbook.objects.filter(item_type=ContentType.objects.get_for_model(SongInSongbook),
                                              item_id=sis.id).count() == 1:
                # If this is the last songbook where the file is in,
                # then delete 
                sis.delete()

            item.delete()
        
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
            rank += 1

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
        return _('"{item_type}" : "{item}", dans le carnet "{songbook}"' \
                 ).format(item=self.item, item_type=self.item_type, songbook=self.songbook)

    class Meta:
        ordering = ["rank"]


class SongInSongbook(SongCommon):

    song = models.ForeignKey(Song,
                             null=True,  # in case of deletion
                             related_name="song_in_songbooks")
    artist = models.ForeignKey("ArtistInSongbook",
                               verbose_name=_("artiste"),
                               related_name="songs_in_songbooks")
    file = models.OneToOneField("FileInSongbook")

        
class ArtistInSongbook(ArtistCommon):

    artist = models.ForeignKey(Artist,
                               null=True,  # in case of deletion
                               related_name="songbooks")

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


class VcsFileCommon(models.Model):

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
        return "{0}:{1}".format(self.object_hash, self.file_path)

    class Meta:
        abstract = True


class GitFile(VcsFileCommon):

    pass


class FileInSongbook(VcsFileCommon):

    pass
