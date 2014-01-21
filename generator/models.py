# -*- coding: utf-8 -*-
import os
from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.conf import settings


song_library = FileSystemStorage(location=settings.SONGS_LIBRARY_DIR)
songbooks_library = FileSystemStorage(location=settings.SONGBOOKS_DIR)

######################################################

class Language(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    
    def __unicode__(self): 
        return self.name
    
    class Meta:
        verbose_name = "langue"    


class Artist(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nom')
    slug = models.SlugField(max_length=100,unique=True)
    
    def __unicode__(self): 
        return self.name
    
    class Meta:
        verbose_name = "artiste"


def get_song_path(song, filename):
    filename = song.slug+'.sg'
    # Put song.sb in SONGS_LIBRARY/<artist-slug>/<filename>
    return os.path.join(song.artist.slug, filename)


class Song(models.Model):
    title = models.CharField(max_length=100,verbose_name='titre')
    slug = models.SlugField(max_length=100,unique=True)
    artist = models.ForeignKey('Artist',verbose_name='artiste')
    language = models.ForeignKey('Language',verbose_name='langue')
    capo = models.IntegerField(null=True,blank=True)

    content_file = models.FileField(storage=song_library,upload_to=get_song_path,verbose_name='contenu')    
    def __unicode__(self): 
        return self.title
    
    class Meta:
        verbose_name = "chant"    

###############################################################

def get_songbook_path(songbook, filename):
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
        verbose_name = "carnet de chants"    
        verbose_name_plural = "carnets de chants"    
        
        
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
        return "Songbook {0}, used by {1}".format(self.songbook,self.user)        
