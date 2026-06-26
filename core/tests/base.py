from datetime import timedelta
import html

from django.test import Client, TestCase, TransactionTestCase, override_settings
from django.utils import timezone

from core.models import Event, Poll

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'


class FactoryMixin:
    @staticmethod
    def future_date(days=14):
        return timezone.now().date() + timedelta(days=days)

    @staticmethod
    def past_date(days=1):
        return timezone.now().date() - timedelta(days=days)

    def make_workshop(self, **kwargs):
        defaults = {
            'title': 'Test Workshop',
            'city': 'Warsaw',
            'date': self.future_date(),
            'description': 'A beginner-friendly English improv workshop.',
            'event_type': Event.WORKSHOP,
            'capacity': 20,
            'is_active': True,
        }
        defaults.update(kwargs)
        return Event.objects.create(**defaults)

    def make_jam(self, **kwargs):
        defaults = {
            'title': 'Friday Night Jam',
            'city': 'Kraków',
            'date': self.future_date(21),
            'description': 'Drop-in English improv jam.',
            'event_type': Event.JAM,
            'capacity': 30,
            'is_active': True,
        }
        defaults.update(kwargs)
        return Event.objects.create(**defaults)

    def make_poll(self, **kwargs):
        defaults = {
            'city': 'Poznań',
            'event_type': Poll.WORKSHOP,
            'description': 'Bring improv to Poznań.',
            'proposed_by_email': 'proposer@example.com',
            'is_active': True,
            'succeeded': False,
        }
        defaults.update(kwargs)
        return Poll.objects.create(**defaults)


class ResponseMixin:
    def response_text(self, response):
        return html.unescape(response.content.decode())

    def assert_page_contains(self, response, text):
        self.assertIn(text, self.response_text(response))


class AcceptanceMixin(FactoryMixin, ResponseMixin):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)

    def register_for_event(self, event, name='Alex Test', email='alex@example.com', *, follow=False):
        return self.client.post(
            f'/events/{event.pk}/register/',
            {'name': name, 'email': email},
            follow=follow,
        )


@override_settings(EMAIL_BACKEND=EMAIL_BACKEND)
class UnitTestCase(FactoryMixin, TestCase):
    pass


@override_settings(EMAIL_BACKEND=EMAIL_BACKEND)
class IntegrationTestCase(FactoryMixin, ResponseMixin, TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)


@override_settings(EMAIL_BACKEND=EMAIL_BACKEND)
class AcceptanceTestCase(AcceptanceMixin, TestCase):
    pass


@override_settings(EMAIL_BACKEND=EMAIL_BACKEND)
class TransactionAcceptanceTestCase(AcceptanceMixin, TransactionTestCase):
    pass