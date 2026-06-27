from django.core.files.uploadedfile import SimpleUploadedFile

from core.models import HomePageContent

from ..base import AcceptanceTestCase

MINIMAL_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
    b"\x01\x01\x01\x00\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


def make_test_image(name="test.png"):
    return SimpleUploadedFile(name, MINIMAL_PNG, content_type="image/png")


class PageAcceptanceTests(AcceptanceTestCase):
    def test_home_page_loads_with_upcoming_events(self):
        self.make_workshop(title="Visible Workshop")

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Visible Workshop")

    def test_events_page_loads_with_workshops_and_jams(self):
        self.make_workshop(title="Browse Workshop")
        self.make_jam(title="Browse Jam")

        response = self.client.get("/events/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Browse Workshop")
        self.assertContains(response, "Browse Jam")

    def test_events_page_filters_by_city(self):
        self.make_workshop(title="Warsaw Event", city="Warsaw")
        self.make_workshop(title="Hidden Event", city="Gdańsk")

        response = self.client.get("/events/", {"city": "Warsaw"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Warsaw Event")
        self.assertNotContains(response, "Hidden Event")

    def test_polls_page_loads_with_active_poll(self):
        self.make_poll(city="Toruń")

        response = self.client.get("/polls/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Toruń")

    def test_home_page_without_hero_image_omits_image_section(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "/media/homepage/")

    def test_home_page_shows_hero_image_when_set(self):
        homepage = HomePageContent.load()
        homepage.hero_image = make_test_image("hero.png")
        homepage.save()

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, homepage.hero_image.url)

    def test_event_card_shows_images_when_set(self):
        event = self.make_workshop(
            title="Image Workshop",
            headline_image=make_test_image("headline.png"),
            description_image=make_test_image("description.png"),
        )

        response = self.client.get("/events/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, event.headline_image.url)
        self.assertContains(response, event.description_image.url)
