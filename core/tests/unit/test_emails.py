from unittest.mock import patch

from django.conf import settings
from django.core import mail

from core.emails import (
    send_poll_expired,
    send_poll_propose_confirm,
    send_poll_success,
    send_poll_vote_confirm,
    send_registration_confirm,
)
from core.models import Registration, Vote

from ..base import UnitTestCase


class RegistrationEmailUnitTests(UnitTestCase):
    def test_send_registration_confirm_builds_expected_message(self):
        event = self.make_workshop(title='Scene Lab', city='Wrocław', venue='Studio A')
        registration = Registration.objects.create(
            event=event,
            name='Taylor',
            email='taylor@example.com',
        )

        result = send_registration_confirm(registration)

        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, ['taylor@example.com'])
        self.assertEqual(message.from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertIn('Scene Lab', message.subject)
        html_body = message.alternatives[0][0]
        self.assertIn('Taylor', html_body)
        self.assertIn('Wrocław', html_body)
        self.assertIn('Studio A', html_body)
        self.assertIn('Taylor', message.body)
        self.assertNotEqual(message.body.strip(), '')

    def test_send_registration_confirm_returns_false_on_smtp_error(self):
        registration = Registration.objects.create(
            event=self.make_workshop(),
            name='Fail',
            email='fail@example.com',
        )

        with patch('core.emails.send_mail', side_effect=Exception('SMTP down')):
            result = send_registration_confirm(registration)

        self.assertFalse(result)


class PollConfirmEmailUnitTests(UnitTestCase):
    def test_send_poll_vote_confirm(self):
        poll = self.make_poll(city='Gdańsk')
        vote = Vote.objects.create(poll=poll, email='voter@example.com')

        self.assertTrue(send_poll_vote_confirm(vote))
        self.assertEqual(mail.outbox[0].to, ['voter@example.com'])
        self.assertIn('Gdańsk', mail.outbox[0].subject)

    def test_send_poll_propose_confirm(self):
        poll = self.make_poll(city='Łódź', proposed_by_email='lead@example.com')

        self.assertTrue(send_poll_propose_confirm(poll))
        self.assertEqual(mail.outbox[0].to, ['lead@example.com'])
        self.assertIn('Łódź', mail.outbox[0].subject)


class PollBroadcastEmailUnitTests(UnitTestCase):
    def test_send_poll_success_emails_voters_and_proposer(self):
        poll = self.make_poll(city='Rzeszów', proposed_by_email='lead@example.com')
        Vote.objects.create(poll=poll, email='voter1@example.com')
        Vote.objects.create(poll=poll, email='voter2@example.com')

        send_poll_success(poll)

        self.assertEqual(len(mail.outbox), 1)
        recipients = set(mail.outbox[0].to)
        self.assertEqual(
            recipients,
            {'voter1@example.com', 'voter2@example.com', 'lead@example.com'},
        )
        self.assertIn('Rzeszów', mail.outbox[0].subject)

    def test_send_poll_success_deduplicates_proposer_who_voted(self):
        poll = self.make_poll(city='Opole', proposed_by_email='lead@example.com')
        Vote.objects.create(poll=poll, email='lead@example.com')

        send_poll_success(poll)

        self.assertEqual(mail.outbox[0].to, ['lead@example.com'])

    def test_send_poll_success_emails_proposer_when_no_votes_yet(self):
        poll = self.make_poll(city='Kielce', proposed_by_email='solo@example.com')

        send_poll_success(poll)

        self.assertEqual(mail.outbox[0].to, ['solo@example.com'])

    def test_send_poll_expired_notifies_participants(self):
        poll = self.make_poll(city='Białystok', proposed_by_email='lead@example.com')
        Vote.objects.create(poll=poll, email='voter@example.com')

        send_poll_expired(poll)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            set(mail.outbox[0].to),
            {'voter@example.com', 'lead@example.com'},
        )
        self.assertIn('Białystok', mail.outbox[0].subject)

    def test_send_poll_expired_emails_proposer_when_no_votes(self):
        poll = self.make_poll(city='Olsztyn', proposed_by_email='solo@example.com')

        send_poll_expired(poll)

        self.assertEqual(mail.outbox[0].to, ['solo@example.com'])