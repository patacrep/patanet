# -*- coding: utf-8 -*-
#    Copyright (C) 2014 The Songbook Team
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

"""Various views"""

from django import template
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView
from django.core.mail.message import BadHeaderError
from django.http.response import Http404
from django.shortcuts import render, redirect


from generator.forms import ContactForm

class FlatPage(TemplateView):
    '''Class handling all the static pages of the app,
    like 'about' or 'FAQ'.
    It try to get and render a template located in 'generator/pages/<url>.html'
    '''
    url = None

    def get_template_names(self):
        try:
            url = self.kwargs['url']
        except KeyError:
            url = str(self.url)
        template_name = 'generator/pages/' + url + '.html'
        try:
            template.loader.get_template(template_name)
            return template_name
        except template.TemplateDoesNotExist:
            raise Http404


def home(request):
    headertitle = _(u'Accueil')
    return render(request, 'generator/home.html', locals())


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            username = None
            if request.user.is_authenticated():
                username = request.user.username
            try:
                form.send_mail(username)
                messages.success(request,
                                 _(u"Votre message a bien été envoyé."))
            except BadHeaderError:
                messages.error(request,
                               _(u"Erreur d'en-tête. Vérifiez le sujet."))
                return render(request, 'generator/contact.html', locals())
            except:
                messages.error(request,
                               _(u"Une erreur s'est produite. Veuillez réessayer."))
                return render(request, 'generator/contact.html', locals())
            return redirect('home')
    else:
        form = ContactForm()
    return render(request, 'generator/contact.html', locals())
