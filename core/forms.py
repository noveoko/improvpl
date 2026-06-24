from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Event, Poll, Registration, Subscriber, Vote


class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email', 'city_interest']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': _('your@email.com'),
                'required': True,
            }),
            'city_interest': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': _('Your city (optional)'),
            }),
        }


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['name', 'email']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': _('Your name'),
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': _('your@email.com'),
                'required': True,
            }),
        }


class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': _('your@email.com'),
                'required': True,
            }),
        }


class PollProposeForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ['proposed_by_email', 'city', 'event_type', 'description']
        widgets = {
            'proposed_by_email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': _('your@email.com'),
                'required': True,
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': _('e.g. Kraków'),
                'required': True,
            }),
            'event_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': _('Why should we bring improv here?'),
                'required': True,
            }),
        }


class JamNotifyForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': _('your@email.com'),
                'required': True,
            }),
        }


class EventFilterForm(forms.Form):
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': _('City'),
        }),
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date',
        }),
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date',
        }),
    )
    event_type = forms.ChoiceField(
        required=False,
        choices=[('', _('All types'))] + Event.EVENT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    skill_level = forms.ChoiceField(
        required=False,
        choices=[('', _('All levels'))] + Event.SKILL_LEVEL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )