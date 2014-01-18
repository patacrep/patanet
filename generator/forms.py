# # -*- coding: utf-8 -*-
from django import forms 
from models import Song
from django.template.defaultfilters import slugify

class SongForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea)
    class Meta:
        model = Song
        fields = ('title','artist','language','capo','content',)
    
    def save(self, force_insert=False, force_update=False, commit=True):
        new_song = super(SongForm, self).save(commit=False)
        new_song.slug = slugify(self.title)
        # Create the content of the file and the filename : SONGS_LIBRARY_DIR/<artist>/<title>.sg
        file_content = self.make_sg_content()
        # Create the file instance for content_file
        new_song.content_file = self.make_sg_file(file_content,new_song.slug)
        if commit:
            new_song.save()
        return new_song

    def make_sg_content(self):
        # TODO: Ajouter les commandes \capo, \beginsong, etc. au champ content
        pass
    
    def make_sg_file(self, file_content,slug):
        # TODO: return a file instance
        filename = slug + '.sg'
        pass        

        
