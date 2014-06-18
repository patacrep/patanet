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


from django import forms
from generator.models import Profile, Song, Songbook
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.core.mail import mail_admins, send_mail
from django.utils.html import escape
from django.conf import settings
from django.contrib.sites.models import Site


class RegisterForm(UserCreationForm):
    """ Require email address when a user signs up """
    email = forms.EmailField(label='Email address',
                             max_length=255,
                             required=True)

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['email'].label = _("Adresse mail")
        self.fields['username'].help_text = _("30 caractères maximum.")
        self.fields['password2'].help_text = None

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            User.objects.get(email=email)
            raise forms.ValidationError(_("Cette adresse mail existe déjà. "
                                "Si vous avez oublié votre mot de passe, "
                                "vous pouvez le réinitialiser."))
        except User.DoesNotExist:
            return email

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


ADMIN_MESSAGE = _(
u'''{user_info} vous a envoyé un message depuis le site {sitename}.

================================================================
{message}
================================================================

Merci de répondre directement à son adresse mail : {sender_mail}'''
)

USER_MESSAGE = _(
u'''Vous avez envoyé un message depuis le site {sitename}. Voici
la copie reçue par les administrateurs.

================================================================
{message}
================================================================

Merci d'utiliser ce site, cordialement,
Les Administrateurs.

PS : Ce message est envoyé automatiquement. Merci de ne pas y répondre,
Les administrateurs prendont contact avec vous.'''
)


class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100,
                              label=_(u"Sujet"))
    sender = forms.EmailField(label=_(u"Votre adresse mail"))
    message = forms.CharField(widget=forms.Textarea,
                              label=_(u"Votre message"))
    send_copy = forms.BooleanField(
                label=_(u"Recevoir une copie du mail"),
                required=False)

    def send_mail(self, username):
        '''Send the contact email. Data should have been cleaned before.
        '''
        message = self._make_admin_message(username)
        subject = self.cleaned_data['subject']
        mail_admins(subject, message, fail_silently=False)

        if self.cleaned_data['send_copy']:
            message = self._make_user_message()
            send_mail(subject,
                      message,
                      settings.DEFAULT_FROM_EMAIL,
                      [self.cleaned_data['sender']])

    def _make_admin_message(self, username):
        '''Adds some information in the message send to the admins
        '''
        if username is not None:
            user_info = username + " (" + self.cleaned_data['sender'] + ") "
        else:
            user_info = self.cleaned_data['sender']

        message = ADMIN_MESSAGE.format(user_info=user_info,
                 sitename=Site.objects.get_current().name,
                 message=escape(self.cleaned_data['message']),
                 sender_mail=self.cleaned_data['sender'])

        return message

    def _make_user_message(self):
        '''Adds some information in the message send to the user
        '''
        message = USER_MESSAGE.format(sitename=Site.objects.get_current().name,
                 message=escape(self.cleaned_data['message']),
                 )

        return message


class SongbookCreationForm(forms.ModelForm):
    class Meta:
        model = Songbook
        fields = ('title', 'description', 'author', 'is_public')

    def save(self, force_insert=False, force_update=False, commit=True):
        new_songbook = super(SongbookCreationForm, self).save(commit=False)
        # User is gotten in the view
        user_profile = Profile.objects.get(user=self.user)
        new_songbook.user = user_profile
        new_songbook.slug = slugify(new_songbook.title)

        if commit:
            new_songbook.save()
        return new_songbook

    def clean_title(self):
        title = self.cleaned_data['title']
        self._clean_latex(title)
        return title

    def clean_description(self):
        description = self.cleaned_data['description']
        self._clean_latex(description)
        return description

    def clean_author(self):
        author = self.cleaned_data["author"]
        self._clean_latex(author)
        return author

    def _clean_latex(self, string):
        '''
        Raise errors if one of the LaTeX special characters
        is in the string
        '''
        TEX_CHAR = ['\\', '{', '}', '&', '[', ']', '^', '~']
        CHARS = ', '.join(['"{char}"'.format(char=char) for char in TEX_CHAR])
        for char in TEX_CHAR:
            if char in string:
                raise forms.ValidationError(
                    _(u"Les caractères suivant sont interdits, "
                    u"merci de les supprimer : {chars}.").format(chars=CHARS))


class SongbookLayoutForm(forms.ModelForm):
    BOOK_OPTIONS = [('diagram', _(u"Diagrammes d'accords")),
            ('importantdiagramonly', _(u"Diagrammes important seulement")),
            ('repeatchords', _(u"Accords sur tous les couplets")),
            ('tabs', _(u"Tablatures")),
            ('lilypond', _(u'Partitions Lilypond')),
            ('pictures', _(u"Couvertures d'albums")),
            ('onesongperpage', _(u"Une chanson par page")),
            ]
    CHORDED = 'chorded'
    LYRICS = 'lyrics'
    BOOK_TYPES = (
        (CHORDED, _('Avec accords')),
        (LYRICS, _('Sans accords')),
        )

    template = forms.CharField(initial='patacrep.tmpl',
                             label=_(u"Mise en forme avec le gabarit")
                             )
    bookoptions = forms.MultipleChoiceField(
                            choices=BOOK_OPTIONS,
                            label=_(u'Options du receuil'),
                            widget=forms.CheckboxSelectMultiple(),
                            required=False
                            )

    class Meta:
        pass
        # model = Layout
        # fields = ('title', 'description', 'is_public', 'booktype')
        # template
