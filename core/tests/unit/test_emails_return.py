from unittest.mock import patch

from core.emails import (
    send_poll_propose_confirm,
    send_poll_vote_confirm,
    send_registration_confirm,
)
from core.models import Registration, Vote

from ..base import UnitTestCase


class EmailReturnValueTests(UnitTestCase):
    def test_send_registration_confirm_returns_true_on_success(self):
        registration = Registration.objects.create(
            event=self.make_workshop(),
            name="Pat",
            email="pat@example.com",
        )

        self.assertTrue(send_registration_confirm(registration))

    def test_send_poll_vote_confirm_returns_true_on_success(self):
        poll = self.make_poll()
        vote = Vote.objects.create(poll=poll, email="voter@example.com")

        self.assertTrue(send_poll_vote_confirm(vote))

    def test_send_poll_propose_confirm_returns_true_on_success(self):
        poll = self.make_poll(proposed_by_email="lead@example.com")

        self.assertTrue(send_poll_propose_confirm(poll))

    def test_send_registration_confirm_returns_false_on_smtp_error(self):
        registration = Registration.objects.create(
            event=self.make_workshop(),
            name="Pat",
            email="pat@example.com",
        )

        with patch("core.emails.send_mail", side_effect=Exception("SMTP down")):
            self.assertFalse(send_registration_confirm(registration))
