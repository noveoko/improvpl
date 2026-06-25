from django.core.mail import send_mail
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Send a test email using current SMTP settings.'

    def add_arguments(self, parser):
        parser.add_argument('recipient', help='Email address to send the test to')

    def handle(self, *args, **options):
        recipient = options['recipient']
        try:
            sent = send_mail(
                'Improv.pl test email',
                'If you received this, Brevo SMTP is working.',
                None,
                [recipient],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f'Sent {sent} message(s) to {recipient}'))
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f'Failed: {exc}'))