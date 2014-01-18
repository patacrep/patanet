# -*- coding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, get_object_or_404
from django.template.defaultfilters import slugify
from django.views.generic import ListView, DetailView, CreateView, FormView
from django.contrib.auth.decorators import login_required

from generator.models import Song, Artist
from generator.forms import SongForm

# Create your views here.

def home(request):
    return render(request, 'generator/generator_base.html',locals())

## User specifics views
#######################
@login_required
def view_profile(request):
    return render(request, 'generator/show_profil.html',locals())

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
        messages.success(self.request, "Votre mot de passe a bien été modifié.")
        return super(FormView, self).form_valid(form)

class PasswordReset(FormView):
    template_name = 'generator/reset_password.html'
    email_template_name = 'generator/reset_password_email.html', # TODO:  Améliorer le template
    subject_template_name = 'Demande de réinitialisation de mot de passe' # TODO: Améliorer le sujet
    form_class = PasswordResetForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Un email de confirmation vous a été envoyé.")
        return super(FormView, self).form_valid(form)


## Songs views
#######################

class SongListByArtist(ListView):
    model = Song
    context_object_name = "liste_chants" 
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
    context_object_name = "liste_auteurs" 
    template_name = "generator/artist_list.html"
    paginate_by = 20
    queryset = Artist.objects.order_by('name')
