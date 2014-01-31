# -*- coding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaultfilters import slugify
from django.views.generic import ListView, DetailView, CreateView, FormView, UpdateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _

from generator.models import Song, Artist, Songbook, Profile
from generator.forms import SongForm, RegisterForm, SongbookOptionsForm
from generator.name_paginator import NamePaginator

##############################################
##############################################

def home(request):
    headertitle = _('Accueil')
    return render(request, 'generator/home.html',locals())

## User specifics views
##############################################
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
    success_url = reverse_lazy('profile')

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
##############################################

class SongList(ListView):
    model = Song
    context_object_name = "song_list" 
    template_name = "generator/song_list.html"
    paginate_by=30
    paginator_class = NamePaginator
    queryset=Song.objects.all().order_by('slug')

class SongListByArtist(ListView):
    model = Song
    context_object_name = "song_list" 
    template_name = "generator/song_list_by_artist.html"
    paginate_by = 10
    
    def get_queryset(self):
        self.artist = get_object_or_404(Artist, slug=self.kwargs['artist'])
        return Song.objects.filter(artist=self.artist).order_by('slug')
    
    def get_context_data(self, **kwargs):
        context = super(SongListByArtist,self).get_context_data(**kwargs)
        context['artist'] = Artist.objects.get(slug=self.kwargs['artist']) 
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
    paginator_class = NamePaginator
    queryset = Artist.objects.order_by('slug')


def random_song(request):
    song=Song.objects.order_by('?')[0]
    return redirect(reverse('show_song', kwargs={'artist':song.artist.slug,'slug':song.slug}))

## Songbooks views
##############################################

class SongbookList(ListView):
    model = Songbook
    context_object_name = "songbooks" 
    template_name = "generator/songbook_list.html"
    
    def get_queryset(self):
        return Songbook.objects.filter(songbooksbyuser__user__user__id=self.request.user.id
                                       ).order_by('is_public','title')
                
    def get_context_data(self, **kwargs):
        context = super(SongbookList, self).get_context_data(**kwargs)
        context['public_songbooks'] = Songbook.objects.filter(is_public=True).order_by('title')
        return context

class NewSongbook(CreateView):
    model = Songbook
    template_name = 'generator/new_songbook.html' 
    form_class = SongbookOptionsForm
    success_url = reverse_lazy('songbook_list')
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(NewSongbook, self).dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        form.user=self.request.user
        messages.success(self.request, _(u"Le nouveau carnet a été créé."))
        return super(NewSongbook, self).form_valid(form)


class UpdateSongbook(UpdateView):
    model = Songbook
    template_name = 'generator/update_songbook.html' 
    form_class = SongbookOptionsForm
    #context_object_name = 'songbook'
    
    def get_success_url(self):
        return reverse('show_songbook',kwargs=self.kwargs)
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UpdateSongbook, self).dispatch(*args, **kwargs)
    
    def get_initial(self):
        initial = super(UpdateSongbook, self).get_initial()
        initial['bookoptions']=self.object.bookoptions
        return initial
    
    def form_valid(self, form):
        form.user=self.request.user
        messages.success(self.request, _(u"Le carnet a été modifié."))
        return super(UpdateSongbook, self).form_valid(form)
        
    
class ShowSongbook(DetailView):
    model=Songbook
    template_name = 'generator/show_songbook.html'
    context_object_name = 'songbook'
    
    def get_queryset(self):
        return Songbook.objects.filter(pk=self.kwargs['pk'],
                                       slug=self.kwargs['slug'])
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ShowSongbook, self).dispatch(*args, **kwargs)

# @login_required
# def add_song_to_songbook(request):
#     """Add a song to the songs list in session.
#     Add this song to a specific songbook.
#     """
#     if (request.GET['song']!=None and request.GET['songbook']!=None): 
#         song_id = request.GET['song']
#         songbook_id = request.GET['songbook']
#         song=Song.objects.get(pk=song_id)
#         songbook=Songbook.objects.get(pk=songbook_id)
#         try:
#             request.session.songs[str(songbook_id)].append(song_id)
#         except KeyError:
#             request.session.songs={str(songbook_id):[song_id]}
#     else:
#         messages.error(request, _("Ce chant ou ce carnet n'existent pas."))
#     return render(request, 'generator/add_song_to_songbook.html',locals())    
