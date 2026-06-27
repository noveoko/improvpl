from unittest.mock import patch

from django.test import override_settings

from core.services import check_poll_after_vote, mark_poll_expired, mark_poll_succeeded

from ..base import UnitTestCase


@override_settings(POLL_VOTE_THRESHOLD=3)
class MarkPollSucceededTests(UnitTestCase):
    @patch("core.services.send_poll_success")
    def test_marks_active_poll_as_succeeded(self, mock_send):
        poll = self.make_poll(vote_count=3)

        result = mark_poll_succeeded(poll)

        poll.refresh_from_db()
        self.assertTrue(result)
        self.assertTrue(poll.succeeded)
        self.assertFalse(poll.is_active)
        mock_send.assert_called_once_with(poll)

    @patch("core.services.send_poll_success")
    def test_returns_false_when_already_succeeded(self, mock_send):
        poll = self.make_poll(succeeded=True, is_active=False)

        result = mark_poll_succeeded(poll)

        self.assertFalse(result)
        mock_send.assert_not_called()

    @patch("core.services.send_poll_success")
    def test_skips_email_when_send_email_false(self, mock_send):
        poll = self.make_poll(vote_count=3)

        mark_poll_succeeded(poll, send_email=False)

        mock_send.assert_not_called()


@override_settings(POLL_VOTE_THRESHOLD=3)
class MarkPollExpiredTests(UnitTestCase):
    @patch("core.services.send_poll_expired")
    def test_closes_active_unsuccessful_poll(self, mock_send):
        poll = self.make_poll(deadline=self.past_date(1))

        result = mark_poll_expired(poll)

        poll.refresh_from_db()
        self.assertTrue(result)
        self.assertFalse(poll.is_active)
        self.assertFalse(poll.succeeded)
        mock_send.assert_called_once_with(poll)

    @patch("core.services.send_poll_expired")
    def test_returns_false_for_inactive_poll(self, mock_send):
        poll = self.make_poll(is_active=False)

        result = mark_poll_expired(poll)

        self.assertFalse(result)
        mock_send.assert_not_called()

    @patch("core.services.send_poll_expired")
    def test_returns_false_for_succeeded_poll(self, mock_send):
        poll = self.make_poll(succeeded=True, is_active=False)

        result = mark_poll_expired(poll)

        self.assertFalse(result)
        mock_send.assert_not_called()


@override_settings(POLL_VOTE_THRESHOLD=2)
class CheckPollAfterVoteTests(UnitTestCase):
    @patch("core.services.mark_poll_succeeded")
    def test_triggers_success_when_threshold_reached(self, mock_mark):
        poll = self.make_poll(vote_count=2)

        check_poll_after_vote(poll)

        mock_mark.assert_called_once_with(poll)

    @patch("core.services.mark_poll_succeeded")
    def test_does_not_trigger_below_threshold(self, mock_mark):
        poll = self.make_poll(vote_count=1)

        check_poll_after_vote(poll)

        mock_mark.assert_not_called()

    @patch("core.services.mark_poll_succeeded")
    def test_ignores_already_succeeded_poll(self, mock_mark):
        poll = self.make_poll(vote_count=5, succeeded=True, is_active=False)

        check_poll_after_vote(poll)

        mock_mark.assert_not_called()
