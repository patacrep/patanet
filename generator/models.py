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
    name = models.CharField(max_length=20, unique=True, null=False)
    code = models.CharField(max_length=6, unique=True, null=False)
    
    def __unicode__(self): 
        return self.name
    
    class Meta:
        verbose_name = "langue"    

class Artist(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Nom')
    slug = models.SlugField(max_length=100, unique=True)
    
    def __unicode__(self): 
        return self.name
    
    class Meta:
        verbose_name = "artiste"

class Song(models.Model):
    title = models.CharField(max_length=100,verbose_name='titre')
    slug = models.SlugField(max_length=100,unique=True)
    artist = models.ForeignKey('Artist',verbose_name='artiste')
    language = models.ForeignKey('Language', verbose_name='langue', null=True)
    capo = models.IntegerField(null=True,blank=True)
    file = models.OneToOneField('GitFile', null=True, unique=True)

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
    
class GitFile(models.Model):
    
    """Hold the information about the file object in a git repository.
    Attributes:
        file_path        string    path of the file in the songs repository
        file_version     string    version of the file as currently known in db
    """
    
    file_path = models.CharField(max_length=500) # not FileField, we take care of the file.
    file_version = models.CharField(max_length=20)
    
    def __unicode__(self):
        return "{0}:{1} (repository {2]".format(self.file_version, self.file_path, self.repo_id)
