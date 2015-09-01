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

"""Users views"""

from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic import CreateView, FormView
from django.core.urlresolvers import reverse_lazy, reverse
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.auth.views import password_reset, password_reset_confirm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


from generator.forms import RegisterForm
from generator.decorators import LoginRequiredMixin
from .songbooks import _set_and_get_current_songbook

class Register(FormView):
    template_name = 'generator/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _(u"Vous êtes à présent inscrit."
                    u"Connectez-vous pour accéder à votre profil."))
        return super(Register, self).form_valid(form)


class PasswordChange(LoginRequiredMixin, FormView):
    template_name = 'generator/user/password_change.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('profile')

    def get_form_kwargs(self):
        kwargs = super(PasswordChange, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request,
                         _(u"Votre mot de passe a bien été modifié.")
                         )
        return super(PasswordChange, self).form_valid(form)


@login_required
def login_complete(request):
    songbooks = request.user.songbooks.all()
    songbook_number = songbooks.count()

    redirect_url = reverse('songbook_private_list')

    if songbook_number == 0:
        messages.success(request, _(u"Bienvenue! "
                                u"Pour commencer, vous pouvez créer un carnet de chant."))
        return redirect(reverse('new_songbook'))
    elif songbook_number == 1:
        songbook = songbooks[0];
        _set_and_get_current_songbook(request, songbook.id)
        messages.success(request, _(u"Carnet de chant '%s' sélectionné.") % songbook.title)
        
        if songbook.count_songs() > 0:
            redirect_url = reverse('show_songbook', kwargs={'id': songbook.id, 'slug': songbook.slug})
        else :
            redirect_url = reverse('artist_list')

    redirect_url = request.GET.get('next', redirect_url)
    return redirect(redirect_url)


def reset_password(request):
    """A wrapper function for password reset"""
    return password_reset(request,
        template_name='generator/password_reset.html',
        email_template_name='generator/password_reset_email.html',
        subject_template_name='generator/password_reset_email_subject.txt',
        post_reset_redirect=reverse('password_reset_done'))


def password_reset_done(request):
    """Only add a message and redirect to home"""
    messages.success(request, _(u"Un email de confirmation vous a été envoyé."))
    return redirect(reverse('home'))


def reset_password_confirm(request, uidb64, token):
    """A wrapper function for password reset confirmation"""
    return  password_reset_confirm(request,
                    uidb64=uidb64,
                    token=token,
                    template_name='generator/password_reset_confirm.html',
                    post_reset_redirect=reverse('password_reset_complete'),
                    extra_context={'uid': uidb64, 'token': token})


def password_reset_complete(request):
    """Only add a message and redirect to home"""
    messages.success(request, _(u"Votre mot de passe a bien été modifié. "
                                u"Connectez-vous pour accéder à votre profil."))
    return redirect(reverse('home'))
