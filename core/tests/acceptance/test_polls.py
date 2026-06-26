from django.core import mail
from django.test import override_settings

from core.models import Poll, Vote

from ..base import AcceptanceTestCase, TransactionAcceptanceTestCase


@override_settings(POLL_VOTE_THRESHOLD=2)
class PollAcceptanceTests(AcceptanceTestCase):
    def test_user_can_propose_a_city_and_receive_confirmation_email(self):
        response = self.client.post(
            '/polls/',
            {
                'form_type': 'propose',
                'proposed_by_email': 'newcity@example.com',
                'city': 'Szczecin',
                'event_type': Poll.WORKSHOP,
                'description': 'Weekly improv in Szczecin.',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        poll = Poll.objects.get(city='Szczecin')
        self.assertEqual(poll.proposed_by_email, 'newcity@example.com')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['newcity@example.com'])
        self.assert_page_contains(response, 'Your proposal is live! Share it to gather votes.')

    def test_user_can_vote_and_receive_confirmation_email(self):
        poll = self.make_poll(city='Katowice')

        response = self.client.post(
            '/polls/',
            {
                'form_type': 'vote',
                'poll_id': poll.pk,
                'email': 'voter@example.com',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        poll.refresh_from_db()
        self.assertEqual(poll.vote_count, 1)
        self.assertTrue(Vote.objects.filter(poll=poll, email='voter@example.com').exists())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['voter@example.com'])
        self.assert_page_contains(response, 'Vote recorded! Thanks for supporting Katowice.')

    def test_poll_succeeds_when_vote_threshold_is_reached(self):
        poll = self.make_poll(city='Lublin', vote_count=1)
        Vote.objects.create(poll=poll, email='first@example.com')

        response = self.client.post(
            '/polls/',
            {
                'form_type': 'vote',
                'poll_id': poll.pk,
                'email': 'second@example.com',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        poll.refresh_from_db()
        self.assertEqual(poll.vote_count, 2)
        self.assertFalse(poll.is_active)
        self.assertTrue(poll.succeeded)


@override_settings(POLL_VOTE_THRESHOLD=2)
class PollDuplicateVoteTests(TransactionAcceptanceTestCase):
    def test_duplicate_vote_is_rejected(self):
        poll = self.make_poll()
        Vote.objects.create(poll=poll, email='repeat@example.com')
        poll.vote_count = 1
        poll.save(update_fields=['vote_count'])
        mail.outbox.clear()

        response = self.client.post(
            '/polls/',
            {
                'form_type': 'vote',
                'poll_id': poll.pk,
                'email': 'repeat@example.com',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        poll.refresh_from_db()
        self.assertEqual(poll.vote_count, 1)
        self.assertEqual(Vote.objects.filter(poll=poll).count(), 1)
        self.assertEqual(len(mail.outbox), 0)
        self.assert_page_contains(response, 'already voted for this city')