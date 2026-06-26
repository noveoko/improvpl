import io

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont

from core.models import Event, HomePageContent

YELLOW = '#FFEB3B'
BLACK = '#111111'
PURPLE = '#7C3AED'
GREEN = '#10B981'


def make_placeholder(label, width, height, bg, fg=BLACK):
    image = Image.new('RGB', (width, height), bg)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), label, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    draw.text(
        ((width - text_w) / 2, (height - text_h) / 2),
        label,
        fill=fg,
        font=font,
    )
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return ContentFile(buffer.getvalue())


class Command(BaseCommand):
    help = 'Attach sample placeholder images to demo events and the homepage (idempotent).'

    def handle(self, *args, **options):
        homepage = HomePageContent.load()
        if not homepage.hero_image:
            homepage.hero_image.save(
                'hero.png',
                make_placeholder('Improv.pl', 1200, 400, YELLOW),
                save=True,
            )
            self.stdout.write('Homepage hero image set.')
        else:
            self.stdout.write('Homepage hero image already set — skipped.')

        workshop = Event.objects.filter(title='English Improv Workshop').first()
        if workshop:
            if not workshop.headline_image:
                workshop.headline_image.save(
                    'headline.png',
                    make_placeholder('Workshop', 800, 320, PURPLE, 'white'),
                    save=True,
                )
                self.stdout.write('Workshop headline image set.')
            if not workshop.description_image:
                workshop.description_image.save(
                    'description.png',
                    make_placeholder('Scenework', 600, 240, YELLOW),
                    save=True,
                )
                self.stdout.write('Workshop description image set.')

        jam = Event.objects.filter(title='Friday Night Improv Jam').first()
        if jam and not jam.headline_image:
            jam.headline_image.save(
                'headline.png',
                make_placeholder('Jam Night', 800, 320, GREEN, 'white'),
                save=True,
            )
            self.stdout.write('Jam headline image set.')

        self.stdout.write(self.style.SUCCESS('Demo images ready. Visit http://127.0.0.1:8000/'))