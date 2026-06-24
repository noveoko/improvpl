from django.conf import settings
from django.utils import timezone

from .emails import send_poll_expired, send_poll_success
from .models import Poll


def mark_poll_succeeded(poll, send_email=True):
    if poll.succeeded:
        return False
    poll.succeeded = True
    poll.is_active = False
    poll.save(update_fields=['succeeded', 'is_active'])
    if send_email:
        send_poll_success(poll)
    return True


def mark_poll_expired(poll, send_email=True):
    if not poll.is_active or poll.succeeded:
        return False
    poll.is_active = False
    poll.save(update_fields=['is_active'])
    if send_email:
        send_poll_expired(poll)
    return True


def check_poll_after_vote(poll):
    threshold = getattr(settings, 'POLL_VOTE_THRESHOLD', 100)
    if poll.vote_count >= threshold and poll.is_active and not poll.succeeded:
        mark_poll_succeeded(poll)


def close_expired_polls(send_email=True):
    today = timezone.now().date()
    threshold = getattr(settings, 'POLL_VOTE_THRESHOLD', 100)
    expired_count = 0
    succeeded_count = 0

    for poll in Poll.objects.filter(is_active=True, succeeded=False):
        poll.reconcile_vote_count()

    for poll in Poll.objects.filter(is_active=True, succeeded=False, vote_count__gte=threshold):
        if mark_poll_succeeded(poll, send_email=send_email):
            succeeded_count += 1

    for poll in Poll.objects.filter(is_active=True, succeeded=False, deadline__lt=today):
        if mark_poll_expired(poll, send_email=send_email):
            expired_count += 1

    return expired_count, succeeded_count