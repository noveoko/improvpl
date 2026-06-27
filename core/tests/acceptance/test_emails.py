from unittest.mock import patch

from core.models import Registration

from ..base import AcceptanceTestCase


class RegistrationEmailFailureAcceptanceTests(AcceptanceTestCase):
    def test_registration_saved_when_confirmation_email_fails(self):
        event = self.make_workshop()

        with patch("core.emails.send_mail", side_effect=Exception("SMTP down")):
            response = self.register_for_event(event, email="saved@example.com", follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Registration.objects.filter(email="saved@example.com").exists())
        self.assert_page_contains(response, "couldn't send the confirmation email")
