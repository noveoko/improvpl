from core.forms import (
    EventFilterForm,
    JamNotifyForm,
    PollProposeForm,
    RegistrationForm,
    SubscriberForm,
    VoteForm,
)
from core.models import Poll, Subscriber

from ..base import UnitTestCase


class RegistrationFormTests(UnitTestCase):
    def test_valid_data(self):
        form = RegistrationForm({'name': 'Alex', 'email': 'alex@example.com'})

        self.assertTrue(form.is_valid())

    def test_requires_name_and_valid_email(self):
        form = RegistrationForm({'name': '', 'email': 'not-an-email'})

        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('email', form.errors)


class SubscriberFormTests(UnitTestCase):
    def test_valid_data(self):
        form = SubscriberForm({'email': 'news@example.com', 'city_interest': 'Warsaw'})

        self.assertTrue(form.is_valid())

    def test_city_interest_is_optional(self):
        form = SubscriberForm({'email': 'news@example.com'})

        self.assertTrue(form.is_valid())

    def test_allows_duplicate_email_because_view_handles_it(self):
        Subscriber.objects.create(email='repeat@example.com')
        form = SubscriberForm({'email': 'repeat@example.com'})

        self.assertTrue(form.is_valid())


class JamNotifyFormTests(UnitTestCase):
    def test_valid_email(self):
        form = JamNotifyForm({'email': 'jamfan@example.com'})

        self.assertTrue(form.is_valid())

    def test_rejects_invalid_email(self):
        form = JamNotifyForm({'email': 'bad'})

        self.assertFalse(form.is_valid())


class VoteFormTests(UnitTestCase):
    def test_valid_email(self):
        form = VoteForm({'email': 'voter@example.com'})

        self.assertTrue(form.is_valid())


class PollProposeFormTests(UnitTestCase):
    def test_valid_proposal(self):
        form = PollProposeForm({
            'proposed_by_email': 'lead@example.com',
            'city': 'Bydgoszcz',
            'event_type': Poll.WORKSHOP,
            'description': 'Bring improv to Bydgoszcz.',
        })

        self.assertTrue(form.is_valid())

    def test_requires_all_fields(self):
        form = PollProposeForm({})

        self.assertFalse(form.is_valid())
        self.assertIn('proposed_by_email', form.errors)
        self.assertIn('city', form.errors)
        self.assertIn('description', form.errors)


class EventFilterFormTests(UnitTestCase):
    def test_empty_filter_is_valid(self):
        form = EventFilterForm({})

        self.assertTrue(form.is_valid())

    def test_accepts_partial_filters(self):
        form = EventFilterForm({
            'city': 'Warsaw',
            'event_type': 'workshop',
            'date_from': self.future_date(1).isoformat(),
            'date_to': self.future_date(30).isoformat(),
            'skill_level': 'beginner',
        })

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['city'], 'Warsaw')
        self.assertEqual(form.cleaned_data['event_type'], 'workshop')
        self.assertEqual(form.cleaned_data['skill_level'], 'beginner')

    def test_rejects_invalid_event_type(self):
        form = EventFilterForm({'event_type': 'concert'})

        self.assertFalse(form.is_valid())
        self.assertIn('event_type', form.errors)