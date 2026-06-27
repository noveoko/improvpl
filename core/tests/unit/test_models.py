from datetime import time, timedelta

from django.test import override_settings
from django.utils import timezone

from core.models import Event, HomePageContent, Poll, Registration, Subscriber, Vote

from ..base import UnitTestCase


class EventModelTests(UnitTestCase):
    def test_str_includes_title_city_and_date(self):
        event = self.make_workshop(title="Scene Lab", city="Gdańsk", date=self.future_date(7))

        self.assertEqual(str(event), f"Scene Lab — Gdańsk ({event.date})")

    def test_is_workshop_and_is_jam(self):
        workshop = self.make_workshop()
        jam = self.make_jam()

        self.assertTrue(workshop.is_workshop)
        self.assertFalse(workshop.is_jam)
        self.assertTrue(jam.is_jam)
        self.assertFalse(jam.is_workshop)

    def test_registration_count_and_spots_remaining(self):
        event = self.make_workshop(capacity=3)
        Registration.objects.create(event=event, name="One", email="one@example.com")
        Registration.objects.create(event=event, name="Two", email="two@example.com")

        self.assertEqual(event.registration_count, 2)
        self.assertEqual(event.spots_remaining, 1)

    def test_is_full_only_applies_to_workshops(self):
        workshop = self.make_workshop(capacity=1)
        Registration.objects.create(event=workshop, name="Full", email="full@example.com")
        jam = self.make_jam(capacity=1)

        self.assertTrue(workshop.is_full)
        self.assertFalse(jam.is_full)

    def test_spots_remaining_never_goes_negative(self):
        event = self.make_workshop(capacity=1)
        Registration.objects.create(event=event, name="One", email="one@example.com")
        Registration.objects.create(event=event, name="Two", email="two@example.com")

        self.assertEqual(event.spots_remaining, 0)


class PollModelTests(UnitTestCase):
    @override_settings(POLL_DEADLINE_DAYS=30)
    def test_save_sets_deadline_when_missing(self):
        poll = Poll(
            city="Lublin",
            description="Weekly improv.",
            proposed_by_email="lead@example.com",
        )
        poll.save()

        expected = (timezone.now() + timedelta(days=30)).date()
        self.assertEqual(poll.deadline, expected)

    def test_save_preserves_explicit_deadline(self):
        deadline = self.future_date(60)
        poll = self.make_poll(deadline=deadline)

        self.assertEqual(poll.deadline, deadline)

    @override_settings(POLL_VOTE_THRESHOLD=50)
    def test_threshold_reads_from_settings(self):
        poll = self.make_poll()

        self.assertEqual(poll.threshold, 50)

    @override_settings(POLL_VOTE_THRESHOLD=10)
    def test_progress_percent_caps_at_100(self):
        poll = self.make_poll(vote_count=25)

        self.assertEqual(poll.progress_percent, 100)

    @override_settings(POLL_VOTE_THRESHOLD=10)
    def test_progress_percent_calculates_correctly(self):
        poll = self.make_poll(vote_count=3)

        self.assertEqual(poll.progress_percent, 30)

    def test_days_remaining_is_zero_after_deadline(self):
        poll = self.make_poll(deadline=self.past_date(3))

        self.assertEqual(poll.days_remaining, 0)

    def test_days_remaining_counts_future_deadlines(self):
        poll = self.make_poll(deadline=self.future_date(5))

        self.assertEqual(poll.days_remaining, 5)

    @override_settings(POLL_VOTE_THRESHOLD=5)
    def test_has_reached_threshold(self):
        below = self.make_poll(vote_count=4)
        at = self.make_poll(city="Katowice", vote_count=5)

        self.assertFalse(below.has_reached_threshold)
        self.assertTrue(at.has_reached_threshold)

    def test_reconcile_vote_count_syncs_drift(self):
        poll = self.make_poll(vote_count=5)
        Vote.objects.create(poll=poll, email="one@example.com")
        Vote.objects.create(poll=poll, email="two@example.com")

        actual = poll.reconcile_vote_count()

        poll.refresh_from_db()
        self.assertEqual(actual, 2)
        self.assertEqual(poll.vote_count, 2)

    def test_str_includes_city_type_and_votes(self):
        poll = self.make_poll(city="Toruń", event_type=Poll.JAM, vote_count=7)

        self.assertEqual(str(poll), "Toruń (jam) — 7 votes")


class RegistrationModelTests(UnitTestCase):
    def test_str_includes_name_email_and_event(self):
        event = self.make_workshop(title="Night Scenes")
        registration = Registration.objects.create(
            event=event,
            name="Pat Lee",
            email="pat@example.com",
        )

        self.assertEqual(str(registration), f"Pat Lee <pat@example.com> — {event}")


class SubscriberModelTests(UnitTestCase):
    def test_str_returns_email(self):
        subscriber = Subscriber.objects.create(email="fan@example.com")

        self.assertEqual(str(subscriber), "fan@example.com")


class VoteModelTests(UnitTestCase):
    def test_str_includes_email_and_poll_city(self):
        poll = self.make_poll(city="Szczecin")
        vote = Vote.objects.create(poll=poll, email="voter@example.com")

        self.assertEqual(str(vote), "voter@example.com — Szczecin")


class EventDefaultsTests(UnitTestCase):
    def test_workshop_defaults(self):
        event = Event.objects.create(
            title="Defaults Workshop",
            city="Warsaw",
            date=self.future_date(),
            description="Test defaults.",
        )

        self.assertEqual(event.event_type, Event.WORKSHOP)
        self.assertEqual(event.skill_level, Event.ALL_LEVELS)
        self.assertEqual(event.capacity, 20)
        self.assertTrue(event.is_active)
        self.assertIsNone(event.start_time)

    def test_event_accepts_optional_start_time(self):
        event = self.make_workshop(start_time=time(19, 30))

        self.assertEqual(event.start_time, time(19, 30))

    def test_event_image_fields_are_optional(self):
        event = self.make_workshop()

        self.assertFalse(event.headline_image)
        self.assertFalse(event.description_image)


class HomePageContentModelTests(UnitTestCase):
    def test_load_returns_singleton(self):
        first = HomePageContent.load()
        second = HomePageContent.load()

        self.assertEqual(first.pk, 1)
        self.assertEqual(second.pk, 1)
        self.assertEqual(HomePageContent.objects.count(), 1)

    def test_save_enforces_singleton_pk(self):
        homepage = HomePageContent()
        homepage.save()

        self.assertEqual(homepage.pk, 1)
