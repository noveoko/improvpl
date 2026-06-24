from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _


def _send_html_email(subject, template_name, context, recipient_list):
    html_message = render_to_string(template_name, context)
    send_mail(
        subject=subject,
        message='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        html_message=html_message,
        fail_silently=False,
    )


def send_registration_confirm(registration):
    _send_html_email(
        subject=_('You\'re registered for %(event)s!') % {'event': registration.event.title},
        template_name='emails/registration_confirm.html',
        context={'registration': registration},
        recipient_list=[registration.email],
    )


def send_poll_vote_confirm(vote):
    _send_html_email(
        subject=_('Vote recorded for %(city)s!') % {'city': vote.poll.city},
        template_name='emails/poll_vote_confirm.html',
        context={'vote': vote},
        recipient_list=[vote.email],
    )


def send_poll_propose_confirm(poll):
    _send_html_email(
        subject=_('Your city proposal for %(city)s is live!') % {'city': poll.city},
        template_name='emails/poll_propose_confirm.html',
        context={'poll': poll},
        recipient_list=[poll.proposed_by_email],
    )


def send_poll_success(poll):
    recipients = list(poll.votes.values_list('email', flat=True).distinct())
    if poll.proposed_by_email not in recipients:
        recipients.append(poll.proposed_by_email)
    if not recipients:
        return
    _send_html_email(
        subject=_('Improv is coming to %(city)s!') % {'city': poll.city},
        template_name='emails/poll_success.html',
        context={'poll': poll},
        recipient_list=recipients,
    )


def send_poll_expired(poll):
    recipients = list(poll.votes.values_list('email', flat=True).distinct())
    if poll.proposed_by_email not in recipients:
        recipients.append(poll.proposed_by_email)
    if not recipients:
        return
    _send_html_email(
        subject=_('Poll for %(city)s has closed') % {'city': poll.city},
        template_name='emails/poll_expired.html',
        context={'poll': poll},
        recipient_list=recipients,
    )