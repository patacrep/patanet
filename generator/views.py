# -*- coding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, get_object_or_404
from django.template.defaultfilters import slugify
from django.views.generic import ListView, DetailView, CreateView, FormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.db.models import Q

from generator.models import Song, Artist, Songbook, Profile
from generator.forms import SongForm, RegisterForm, SongbookOptionsForm

import json
# Create your views here.

def home(request):
    headertitle = _('Accueil')
    return render(request, 'generator/generator_base.html',locals())

## User specifics views
#######################
@login_required
def view_profile(request):
    profile = Profile.objects.get(user=request.user)
    return render(request, 'generator/show_profile.html',locals())

class Register(CreateView):
    template_name = 'generator/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('home')
    
    def form_valid(self, form):
        user = form.save()
        profile = Profile(user=user)
        profile.save()
        messages.success(self.request, _(u"Vous êtes à présent inscrit." 
                    u"Connectez-vous pour accéder à votre profil."))
        return super(CreateView, self).form_valid(form)
    
class PasswordChange(FormView):
    template_name = 'generator/password_change.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('profil')

    def get_form_kwargs(self):
        kwargs = super(PasswordChange, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _(u"Votre mot de passe a bien été modifié."))
        return super(FormView, self).form_valid(form)
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PasswordChange, self).dispatch(*args, **kwargs)

class PasswordReset(FormView):
    template_name = 'generator/password_reset.html'
    email_template_name = 'generator/password_reset_email.html', # TODO:  Améliorer le template
    subject_template_name = 'generator/password_reset_email_subject.txt' # TODO: Améliorer le sujet
    form_class = PasswordResetForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _(u"Un email de confirmation vous a été envoyé."))
        return super(FormView, self).form_valid(form)


class PasswordResetConfirm(FormView): # TODO: Tester si ça fonctionne
    template_name = 'generator/password_reset_confirm.html'
    form_class = SetPasswordForm
    success_url = reverse_lazy('profil')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _("Votre mot de passe a bien été modifié."))
        return super(FormView, self).form_valid(form)


## Songs views
#######################

class SongListByArtist(ListView):
    model = Song
    context_object_name = "song_list" 
    template_name = "generator/song_list_by_artist.html"
    paginate_by = 10
    
    def get_queryset(self):
        self.artist = get_object_or_404(Artist, slug=self.kwargs['artist'])
        return Song.objects.filter(artist=self.artist)
    
    def get_context_data(self, **kwargs):
        context = super(SongListByArtist,self).get_context_data(**kwargs)
        context['artist'] = Artist.objects.get(slug=self.kwargs['artist']) 
        # FIXME: Si l'objet n'existe pas ? Déjà géré par le get_object_or_404 ?
        return context


class SongView(DetailView):
    context_object_name = "song" 
    model = Song
    template_name = "generator/show_song.html"

    def get_queryset(self):
        return Song.objects.filter(artist__slug=self.kwargs['artist'],slug=self.kwargs['slug'])


class ArtistList(ListView):
    model = Artist
    context_object_name = "artist_list" 
    template_name = "generator/artist_list.html"
    paginate_by = 20
    queryset = Artist.objects.order_by('name')

## Songbooks views
#######################

class SongbookList(ListView):
    model = Songbook
    context_object_name = "songbooks" 
    template_name = "generator/songbook_list.html"
    
    def get_queryset(self):
        return Songbook.objects.filter(songbooksbyuser__user__user=self.request.user).order_by('is_public','title')
                
    def get_context_data(self, **kwargs):
        context = super(SongbookList, self).get_context_data(**kwargs)
        context['public_songbooks'] = Songbook.objects.filter(is_public=True).order_by('title')
        return context

class NewSongbook(CreateView):
    model = Songbook
    template_name = 'generator/songbook_options.html' 
    form_class = SongbookOptionsForm
    success_url = reverse_lazy('songbook_list')
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(NewSongbook, self).dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        form.user=self.request.user
        messages.success(self.request, _(u"Le nouveau receuil a été créé."))
        return super(NewSongbook, self).form_valid(form)
    
    
class ShowSongbook(DetailView):
    model=Songbook
    template_name = 'generator/show_songbook.html'
    songbook_options={}
    context_object_name = 'songbook'
    
    def get_object(self):
        songbook = super(ShowSongbook, self).get_object()
        options = songbook.content_file.read()
        self.songbook_options=json.loads(options)
        return songbook
    
    def get_queryset(self):
        return Songbook.objects.filter(pk=self.kwargs['pk'],
                                       slug=self.kwargs['slug']
                                       )
    
    def get_context_data(self, **kwargs):
        context = super(ShowSongbook, self).get_context_data(**kwargs)        
        context['options'] = self.songbook_options
        return context
    
    