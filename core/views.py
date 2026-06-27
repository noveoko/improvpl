from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from .emails import send_poll_propose_confirm, send_poll_vote_confirm, send_registration_confirm
from .forms import (
    EventFilterForm,
    JamNotifyForm,
    PollProposeForm,
    RegistrationForm,
    SubscriberForm,
    VoteForm,
)
from .models import Event, HomePageContent, Poll, Subscriber
from .services import check_poll_after_vote


def home(request):
    upcoming_events = Event.objects.filter(
        is_active=True,
        date__gte=timezone.now().date(),
    )[:4]
    active_polls = Poll.objects.filter(is_active=True, succeeded=False)[:2]
    subscriber_form = SubscriberForm()

    if request.method == "POST" and request.POST.get("form_type") == "subscribe":
        subscriber_form = SubscriberForm(request.POST)
        if subscriber_form.is_valid():
            _subscriber, created = Subscriber.objects.get_or_create(
                email=subscriber_form.cleaned_data["email"],
                defaults={
                    "city_interest": subscriber_form.cleaned_data.get("city_interest", ""),
                },
            )
            if created:
                messages.success(request, _("You're on the list! We'll keep you posted."))
            else:
                messages.info(request, _("You're already subscribed — thanks!"))
            return redirect("home")

    return render(
        request,
        "home.html",
        {
            "homepage": HomePageContent.load(),
            "upcoming_events": upcoming_events,
            "active_polls": active_polls,
            "subscriber_form": subscriber_form,
        },
    )


def events_list(request):
    events = Event.objects.filter(is_active=True, date__gte=timezone.now().date())
    filter_form = EventFilterForm(request.GET or None)

    if filter_form.is_valid():
        city = filter_form.cleaned_data.get("city")
        date_from = filter_form.cleaned_data.get("date_from")
        date_to = filter_form.cleaned_data.get("date_to")
        event_type = filter_form.cleaned_data.get("event_type")
        skill_level = filter_form.cleaned_data.get("skill_level")

        if city:
            events = events.filter(city__icontains=city)
        if date_from:
            events = events.filter(date__gte=date_from)
        if date_to:
            events = events.filter(date__lte=date_to)
        if event_type:
            events = events.filter(event_type=event_type)
        if skill_level:
            events = events.filter(skill_level=skill_level)

    cities = Event.objects.filter(is_active=True).values_list("city", flat=True).distinct()

    return render(
        request,
        "events.html",
        {
            "events": events,
            "filter_form": filter_form,
            "cities": sorted(set(cities)),
            "registration_form": RegistrationForm(),
            "jam_notify_form": JamNotifyForm(),
        },
    )


@require_POST
def event_register(request, event_id):
    event = get_object_or_404(Event, pk=event_id, is_active=True)

    if not event.is_workshop:
        messages.error(request, _("Jams are drop-in — no registration needed!"))
        return redirect("events_list")

    if event.is_full:
        messages.error(request, _("Sorry, this workshop is full."))
        return redirect("events_list")

    form = RegistrationForm(request.POST)
    if not form.is_valid():
        messages.error(request, _("Please check your name and email."))
        return redirect("events_list")

    registration = form.save(commit=False)
    registration.event = event
    try:
        registration.save()
    except IntegrityError:
        messages.info(request, _("You're already registered for this event."))
        return redirect("events_list")

    if send_registration_confirm(registration):
        messages.success(
            request,
            _("You're in! Check your email for confirmation."),
        )
    else:
        messages.warning(
            request,
            _(
                "You're registered, but we couldn't send the confirmation email. We'll see you there!"
            ),
        )
    return redirect("events_list")


@require_POST
def jam_notify(request, event_id):
    event = get_object_or_404(Event, pk=event_id, is_active=True, event_type=Event.JAM)
    form = JamNotifyForm(request.POST)

    if form.is_valid():
        _subscriber, created = Subscriber.objects.get_or_create(
            email=form.cleaned_data["email"],
            defaults={"city_interest": event.city},
        )
        if created:
            messages.success(request, _("We'll notify you of any changes."))
        else:
            messages.info(request, _("You're already on our list — we'll keep you posted!"))

    return redirect("events_list")


def polls_list(request):
    active_polls = Poll.objects.filter(is_active=True, succeeded=False)
    closed_polls = Poll.objects.filter(is_active=False).order_by("-created_at")

    propose_form = PollProposeForm()
    vote_form = VoteForm()

    if request.method == "POST":
        if request.POST.get("form_type") == "propose":
            propose_form = PollProposeForm(request.POST)
            if propose_form.is_valid():
                poll = propose_form.save()
                if send_poll_propose_confirm(poll):
                    messages.success(
                        request,
                        _("Your proposal is live! Share it to gather votes."),
                    )
                else:
                    messages.warning(
                        request,
                        _("Your proposal is live, but we couldn't send a confirmation email."),
                    )
                return redirect("polls_list")
        elif request.POST.get("form_type") == "vote":
            poll_id = request.POST.get("poll_id")
            poll = get_object_or_404(Poll, pk=poll_id, is_active=True, succeeded=False)
            vote_form = VoteForm(request.POST)
            if vote_form.is_valid():
                vote = vote_form.save(commit=False)
                vote.poll = poll
                try:
                    vote.save()
                    poll.vote_count += 1
                    poll.save(update_fields=["vote_count"])
                    check_poll_after_vote(poll)
                    if send_poll_vote_confirm(vote):
                        messages.success(
                            request,
                            _("Vote recorded! Thanks for supporting %(city)s.")
                            % {"city": poll.city},
                        )
                    else:
                        messages.success(
                            request,
                            _("Vote recorded for %(city)s! (Confirmation email could not be sent.)")
                            % {"city": poll.city},
                        )
                except IntegrityError:
                    messages.info(request, _("You've already voted for this city."))
                return redirect("polls_list")

    return render(
        request,
        "polls.html",
        {
            "active_polls": active_polls,
            "closed_polls": closed_polls,
            "propose_form": propose_form,
            "vote_form": vote_form,
        },
    )
