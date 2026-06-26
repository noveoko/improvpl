from io import StringIO

from django.core.management import call_command
from django.test import override_settings

from core.models import Vote

from ..base import IntegrationTestCase


@override_settings(POLL_VOTE_THRESHOLD=2)
class ClosePollsCommandIntegrationTests(IntegrationTestCase):
    def test_close_polls_command_reports_counts(self):
        winning_poll = self.make_poll(vote_count=2, proposed_by_email='win@example.com')
        Vote.objects.create(poll=winning_poll, email='one@example.com')
        Vote.objects.create(poll=winning_poll, email='two@example.com')
        self.make_poll(
            city='Expired',
            deadline=self.past_date(1),
            proposed_by_email='exp@example.com',
        )

        out = StringIO()
        call_command('close_polls', stdout=out)

        output = out.getvalue()
        self.assertIn('Done. Expired: 1, Succeeded: 1', output)

    def test_close_polls_dry_run_updates_polls_without_sending_email(self):
        from django.core import mail

        poll = self.make_poll(
            vote_count=2,
            proposed_by_email='win@example.com',
        )
        Vote.objects.create(poll=poll, email='one@example.com')
        Vote.objects.create(poll=poll, email='two@example.com')

        out = StringIO()
        call_command('close_polls', '--dry-run', stdout=out)

        poll.refresh_from_db()
        self.assertTrue(poll.succeeded)
        self.assertFalse(poll.is_active)
        self.assertEqual(len(mail.outbox), 0)
        self.assertIn('Dry run', out.getvalue())