# -*- coding: utf-8 -*-
import os
from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

song_library = FileSystemStorage(location=settings.SONGS_LIBRARY_DIR)
songbooks_library = FileSystemStorage(location=settings.SONGBOOKS_DIR)

######################################################

class Language(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    
    def __unicode__(self): 
        return self.name
    
    class Meta:
        verbose_name = _("langue")    


class Artist(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nom')
    slug = models.SlugField(max_length=100,unique=True)
    
    def __unicode__(self): 
        return self.name
    
    class Meta:
        verbose_name = _("artiste")


def get_song_path(song, filename):
    filename = song.slug+'.sg'
    # Put song.sb in SONGS_LIBRARY/<artist-slug>/<filename>
    return os.path.join(song.artist.slug, filename)


class Song(models.Model):
    title = models.CharField(max_length=100,verbose_name=_('titre'))
    slug = models.SlugField(max_length=100,unique=True) # FIXME: cas de deux chants de même slug et d'artistes différents ...
    artist = models.ForeignKey('Artist',verbose_name=_('artiste'))
    language = models.ForeignKey('Language',verbose_name=_('langue'))
    capo = models.IntegerField(null=True,blank=True)

    content_file = models.FileField(storage=song_library,upload_to=get_song_path,verbose_name=_('contenu'))    
    def __unicode__(self): 
        return self.title
    
    class Meta:
        verbose_name = _("chant")    

###############################################################

def get_songbook_path(songbook, filename):
    # TODO: Utiliser slugify plutôt pour être sûr de virer les caractère exotiques
    user_directory = songbook.user.username.replace(' ','_') 
    filename = songbook.title.replace(' ','_')+".sb"
    return os.path.join(user_directory, filename)
    
    
class Songbook(models.Model):
    title = models.CharField(max_length=100)  
    description = models.TextField(blank=True)
    
    content_file = models.FileField(storage=songbooks_library,upload_to=get_songbook_path)
    
    def __unicode__(self): 
        return self.title
    
    class Meta:
        verbose_name = _("carnet de chants")    
        verbose_name_plural = _("carnets de chants")    
        
        
###############################################################

class Profile(models.Model):
    user = models.OneToOneField(User)
    songbooks = models.ManyToManyField(Songbook,blank=True,through='SongbooksByUser')    
    
    def __unicode__(self): 
        return self.name       


class SongbooksByUser(models.Model):
    is_owner = models.BooleanField(default=False)
    user = models.ForeignKey('Profile')
    songbook = models.ForeignKey('Songbook')

    def __unicode__(self): 
        return _("Songbook {0}, used by {1}").format(self.songbook,self.user)        
