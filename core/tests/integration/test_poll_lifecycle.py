from django.core import mail
from django.test import override_settings

from core.models import Poll, Vote
from core.services import close_expired_polls

from ..base import IntegrationTestCase


@override_settings(POLL_VOTE_THRESHOLD=2)
class CloseExpiredPollsIntegrationTests(IntegrationTestCase):
    def test_closes_polls_past_deadline_and_sends_expired_email(self):
        poll = self.make_poll(
            city='Expired City',
            deadline=self.past_date(2),
            proposed_by_email='lead@example.com',
        )
        Vote.objects.create(poll=poll, email='voter@example.com')

        expired_count, succeeded_count = close_expired_polls()

        poll.refresh_from_db()
        self.assertEqual(expired_count, 1)
        self.assertEqual(succeeded_count, 0)
        self.assertFalse(poll.is_active)
        self.assertFalse(poll.succeeded)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Expired City', mail.outbox[0].subject)

    def test_finalizes_polls_at_threshold_and_sends_success_email(self):
        poll = self.make_poll(
            city='Winning City',
            vote_count=2,
            proposed_by_email='lead@example.com',
        )
        Vote.objects.create(poll=poll, email='voter@example.com')
        Vote.objects.create(poll=poll, email='voter2@example.com')

        expired_count, succeeded_count = close_expired_polls()

        poll.refresh_from_db()
        self.assertEqual(expired_count, 0)
        self.assertEqual(succeeded_count, 1)
        self.assertTrue(poll.succeeded)
        self.assertFalse(poll.is_active)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Winning City', mail.outbox[0].subject)

    def test_reconciles_vote_count_drift_before_closing(self):
        poll = self.make_poll(vote_count=99, deadline=self.past_date(1))
        Vote.objects.create(poll=poll, email='only@example.com')

        close_expired_polls(send_email=False)

        poll.refresh_from_db()
        self.assertEqual(poll.vote_count, 1)
        self.assertFalse(poll.is_active)

    def test_send_email_false_skips_notifications(self):
        self.make_poll(vote_count=2, proposed_by_email='lead@example.com')
        self.make_poll(deadline=self.past_date(1), proposed_by_email='lead2@example.com')

        close_expired_polls(send_email=False)

        self.assertEqual(len(mail.outbox), 0)


@override_settings(POLL_VOTE_THRESHOLD=2)
class PollVoteToSuccessIntegrationTests(IntegrationTestCase):
    def test_vote_via_view_triggers_success_emails_at_threshold(self):
        poll = self.make_poll(city='Threshold City', vote_count=1)
        Vote.objects.create(poll=poll, email='first@example.com')
        mail.outbox.clear()

        response = self.client.post(
            '/polls/',
            {
                'form_type': 'vote',
                'poll_id': poll.pk,
                'email': 'second@example.com',
            },
            follow=True,
        )

        poll.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(poll.succeeded)
        self.assertFalse(poll.is_active)
        self.assertGreaterEqual(len(mail.outbox), 2)
        subjects = [message.subject for message in mail.outbox]
        self.assertTrue(any('Threshold City' in subject for subject in subjects))