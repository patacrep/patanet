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

from generator.models import Song, Artist, Songbook, Profile, ItemsInSongbook,\
    Section
from generator.forms import SongForm, RegisterForm, SongbookOptionsForm
from generator.name_paginator import NamePaginator
from django.views.generic.edit import DeleteView
from django.contrib.auth.views import password_reset, password_reset_confirm

##############################################
##############################################

def home(request):
    headertitle = _('Accueil')
    return render(request, 'generator/home.html',locals())

## Decorators
##############################################
def render_with_current_songbook(View):
    def wrapper(previous_function):
        def add_songbook_to_context(self, **kwargs):
            context = previous_function(self, **kwargs)
            context['show_current_songbook'] = True
            try:
                songbook = Songbook.objects.get(id=self.request.session['current_songbook'])
                context['current_songbook'] = songbook
                current_item_list=ItemsInSongbook.objects.filter(songbook=songbook).order_by('rank')
                context['current_item_list'] = current_item_list
                
                if songbook.count_section() > 1:
                    context['multi_section'] = True
                    context['first_section'] = current_item_list.filter(item_type__model='section')[0]
                if songbook.count_section() > 0:
                    context['sb_has_section'] = True
                    
            except (KeyError, Songbook.DoesNotExist):
                pass
            return context
        return add_songbook_to_context
    
    View.get_context_data = wrapper(View.get_context_data)
    
    return View

def login_required_or_is_public(View):
    def wrapper(previous_function):
        def check_public(self, *args, **kwargs):
            if View.get_object(self).is_public:
                return previous_function(self, *args, **kwargs)
            else:
                return method_decorator(login_required)(previous_function)(self, *args, **kwargs)
        return check_public
    
    View.dispatch = wrapper(View.dispatch)
    
    return View

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

def reset_password(request):
    """A wrapper function for password reset"""
    return password_reset(request, template_name='generator/password_reset.html',
        email_template_name='generator/password_reset_email.html',
        subject_template_name='generator/password_reset_email_subject.txt',
        post_reset_redirect=reverse('password_reset_done'))

def password_reset_done(request):
    """Only add a message and redirect to home"""
    messages.success(request, _("Un email de confirmation vous a été envoyé."))
    return redirect(reverse('home'))

def reset_password_confirm(request, uidb64, token):
    """A wrapper function for password reset confirmation"""
    return  password_reset_confirm(request, 
                                   uidb64=uidb64,
                                   token=token,
                                   template_name='generator/password_reset_confirm.html',
                                   post_reset_redirect = reverse('password_reset_complete'),
                                   extra_context={'uid':uidb64,'token':token})

def password_reset_complete(request):
    """Only add a message and redirect to home"""
    messages.success(request, _("Votre mot de passe a bien été modifié. Connectez-vous pour accéder à votre profil."))
    return redirect(reverse('home'))

## Songs views
##############################################
@render_with_current_songbook
class SongList(ListView):
    model = Song
    context_object_name = "song_list" 
    template_name = "generator/song_list.html"
    paginate_by = 10
    paginator_class = NamePaginator
    queryset=Song.objects.all().order_by('slug')
    
@render_with_current_songbook
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

@render_with_current_songbook
class SongView(DetailView):
    context_object_name = "song" 
    model = Song
    template_name = "generator/show_song.html"

    def get_queryset(self):
        return Song.objects.filter(artist__slug=self.kwargs['artist'],slug=self.kwargs['slug'])

@render_with_current_songbook
class ArtistList(ListView):
    model = Artist
    context_object_name = "artist_list" 
    template_name = "generator/artist_list.html"
    paginate_by = 10
    paginator_class = NamePaginator
    queryset = Artist.objects.order_by('slug')

def random_song(request):
    song=Song.objects.order_by('?')[0]
    return redirect(reverse('show_song', kwargs={'artist':song.artist.slug,'slug':song.slug}))

## Songbooks views
##############################################

class SongbookPublicList(ListView):
    model = Songbook
    context_object_name = "songbooks" 
    template_name = "generator/songbook_public_list.html"
    
    def get_queryset(self):
        return Songbook.objects.filter(is_public=True
                                       ).order_by('title')

class SongbookPrivateList(ListView):
    model = Songbook
    context_object_name = "songbooks" 
    template_name = "generator/songbook_private_list.html"
    
    def get_queryset(self):
        return Songbook.objects.filter(songbooksbyuser__user__user__id=self.request.user.id
                                       ).order_by('title')


class NewSongbook(CreateView):
    model = Songbook
    template_name = 'generator/new_songbook.html' 
    form_class = SongbookOptionsForm
    success_url = reverse_lazy('songbook_private_list')
    
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
        self.kwargs["slug"] = self.object.slug
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
        
@login_required_or_is_public
class ShowSongbook(DetailView):
    model=Songbook
    template_name = 'generator/show_songbook.html'
    context_object_name = 'songbook'
    
    def get_queryset(self):
        return Songbook.objects.filter(id=self.kwargs['id'],
                                       slug=self.kwargs['slug'])
    


@login_required
def set_current_songbook(request):
    """Set a songbook for edition with sessions
     """
    if (request.GET['songbook']!=None): 
        songbook_id = request.GET['songbook']
        request.session['current_songbook'] = int(songbook_id)
        return redirect('song_list')
    else:
        messages.error(request, _("Ce carnet n'existe pas."))
        return redirect('songbook_list')
    

def _add_item(item,songbook,rank,current_item_list):
    """Add an item to a songbook.
    Return True if it has been added, false if not.
    """
    if item not in current_item_list:
        item_in_songbook = ItemsInSongbook(item=item,
                                            songbook=songbook,
                                            rank=rank)
        item_in_songbook.save()
        return True
    else:
        return False

def get_new_rank(songbook_id):
        """Get the last song in the section, and return this rank plus 1."""
        rank = ItemsInSongbook.objects.filter(songbook=songbook_id).count()
        if rank == None:
            return 1
        else:
            return rank + 1

@login_required
def add_songs_to_songbook(request):
    """Add a list of songs to the itmes of the current songbook.
    """ 
    next_url=request.POST['next']
        
    try:
        songbook_id = request.session['current_songbook']
        songbook = Songbook.objects.get(id=songbook_id)
    except (KeyError, Songbook.DoesNotExist):
        messages.error(request, _("Choisissez un carnet pour ajouter ces chants"))
        return redirect(next_url)
    
    song_list = request.POST.getlist('songs[]')
    current_item_list = songbook.items.all()
    rank=get_new_rank(songbook_id)
    
    for song_id in song_list:
        try:    
            song=Song.objects.get(id=song_id)
            added = _add_item(item=song,
                              songbook=songbook,
                              rank=rank,
                              current_item_list=current_item_list)
            if added:
                rank+=1
        except Song.DoesNotExist: # May be useless
            pass
        
    artist_list = request.POST.getlist('artists[]')
    for artist_id in artist_list:
        try:
            artist=Artist.objects.get(id=artist_id)
            song_list=artist.songs.all()
            for song in song_list:
                added = _add_item(item=song,
                              songbook=songbook,
                              rank=rank,
                              current_item_list=current_item_list)
                if added:
                    rank+=1
        except Artist.DoesNotExist:
            pass
        
    return redirect(next_url)


class DeleteSongbook(DeleteView):
    model = Songbook
    context_object_name = "songbook" 
    template_name = 'generator/delete_songbook.html' 
    success_url = reverse_lazy('profile')
    
    def get_object(self, queryset=None):
        id = self.kwargs.get('id', None)
        slug = self.kwargs.get('slug', None)
        return get_object_or_404(Songbook, id=id, slug=slug)
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteSongbook, self).dispatch(*args, **kwargs)

