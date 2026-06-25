from datetime import time, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Event, Poll


class Command(BaseCommand):
    help = 'Create sample events and polls for the homepage (idempotent).'

    def handle(self, *args, **options):
        today = timezone.now().date()

        events = [
            {
                'title': 'English Improv Workshop',
                'city': 'Warsaw',
                'venue': 'Centrum Kreatywności',
                'date': today + timedelta(days=14),
                'start_time': time(18, 30),
                'event_type': Event.WORKSHOP,
                'skill_level': Event.BEGINNER,
                'capacity': 20,
                'description': (
                    'A beginner-friendly English improv workshop. '
                    'Games, scenework, and lots of laughs. No experience needed.'
                ),
                'instructor': 'Alex Morgan',
            },
            {
                'title': 'Friday Night Improv Jam',
                'city': 'Kraków',
                'venue': 'Kulturalna Scena',
                'date': today + timedelta(days=21),
                'start_time': time(19, 0),
                'event_type': Event.JAM,
                'skill_level': Event.ALL_LEVELS,
                'capacity': 30,
                'description': (
                    'Drop-in English improv jam. Come play, watch, or both. '
                    'All skill levels welcome.'
                ),
                'instructor': '',
            },
            {
                'title': 'Scenework Intensive',
                'city': 'Wrocław',
                'venue': 'Teatr Studio',
                'date': today + timedelta(days=35),
                'start_time': time(17, 0),
                'event_type': Event.WORKSHOP,
                'skill_level': Event.INTERMEDIATE,
                'capacity': 16,
                'description': (
                    'Two hours of scenework drills for improvisers with some stage time. '
                    'English only.'
                ),
                'instructor': 'Jamie Lee',
            },
        ]

        polls = [
            {
                'city': 'Wrocław',
                'event_type': Poll.WORKSHOP,
                'description': 'Bring a weekly English improv workshop to Wrocław.',
                'proposed_by_email': 'hello@improv.pl',
                'vote_count': 42,
            },
            {
                'city': 'Gdańsk',
                'event_type': Poll.JAM,
                'description': 'Monthly English improv jam by the coast — who\'s in?',
                'proposed_by_email': 'hello@improv.pl',
                'vote_count': 28,
            },
        ]

        created_events = 0
        for data in events:
            _, created = Event.objects.get_or_create(
                title=data['title'],
                city=data['city'],
                date=data['date'],
                defaults=data,
            )
            if created:
                created_events += 1

        created_polls = 0
        for data in polls:
            _, created = Poll.objects.get_or_create(
                city=data['city'],
                event_type=data['event_type'],
                defaults=data,
            )
            if created:
                created_polls += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Demo data ready. New events: {created_events}, new polls: {created_polls}.'
            )
        )