from django.core import mail

from core.models import Registration

from ..base import AcceptanceTestCase, TransactionAcceptanceTestCase


class EventRegistrationAcceptanceTests(AcceptanceTestCase):
    def test_successful_workshop_registration_sends_confirmation_email(self):
        event = self.make_workshop(title='English Improv Workshop')

        response = self.register_for_event(
            event,
            name='Jamie Lee',
            email='jamie@example.com',
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Registration.objects.count(), 1)
        registration = Registration.objects.get()
        self.assertEqual(registration.event, event)
        self.assertEqual(registration.name, 'Jamie Lee')
        self.assertEqual(registration.email, 'jamie@example.com')

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['jamie@example.com'])
        self.assertIn('English Improv Workshop', mail.outbox[0].subject)
        self.assert_page_contains(response, 'Check your email for confirmation')

    def test_full_workshop_rejects_new_registration(self):
        event = self.make_workshop(capacity=2)
        Registration.objects.create(event=event, name='One', email='one@example.com')
        Registration.objects.create(event=event, name='Two', email='two@example.com')

        response = self.register_for_event(event, email='three@example.com', follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Registration.objects.count(), 2)
        self.assertEqual(len(mail.outbox), 0)
        self.assert_page_contains(response, 'Sorry, this workshop is full.')

    def test_jam_registration_is_not_allowed(self):
        event = self.make_jam()

        response = self.register_for_event(event, email='jammer@example.com', follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Registration.objects.exists())
        self.assertEqual(len(mail.outbox), 0)
        self.assert_page_contains(response, 'Jams are drop-in')

    def test_invalid_registration_data_is_rejected(self):
        event = self.make_workshop()

        response = self.client.post(
            f'/events/{event.pk}/register/',
            {'name': '', 'email': 'not-an-email'},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Registration.objects.exists())
        self.assertEqual(len(mail.outbox), 0)
        self.assert_page_contains(response, 'Please check your name and email.')

    def test_inactive_event_returns_404(self):
        event = self.make_workshop(is_active=False)

        response = self.register_for_event(event)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(Registration.objects.exists())

    def test_get_request_is_not_allowed(self):
        event = self.make_workshop()

        response = self.client.get(f'/events/{event.pk}/register/')

        self.assertEqual(response.status_code, 405)
        self.assertFalse(Registration.objects.exists())


class EventRegistrationDuplicateTests(TransactionAcceptanceTestCase):
    def test_duplicate_registration_is_rejected_without_second_email(self):
        event = self.make_workshop()
        self.register_for_event(event, email='repeat@example.com')
        mail.outbox.clear()

        response = self.register_for_event(
            event,
            name='Someone Else',
            email='repeat@example.com',
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Registration.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 0)
        self.assert_page_contains(response, 'already registered for this event')