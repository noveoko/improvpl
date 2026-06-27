from core.models import Event, Registration

from ..base import IntegrationTestCase


class HomeViewIntegrationTests(IntegrationTestCase):
    def test_shows_only_active_upcoming_events(self):
        self.make_workshop(title="Visible Workshop")
        self.make_workshop(title="Past Workshop", date=self.past_date(3))
        self.make_workshop(title="Inactive Workshop", is_active=False)

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Visible Workshop")
        self.assertNotContains(response, "Past Workshop")
        self.assertNotContains(response, "Inactive Workshop")

    def test_limits_homepage_to_four_events(self):
        for index in range(6):
            self.make_workshop(title=f"Workshop {index}", date=self.future_date(index + 1))

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Workshop 0")
        self.assertNotContains(response, "Workshop 5")


class EventsListFilterIntegrationTests(IntegrationTestCase):
    def setUp(self):
        super().setUp()
        self.warsaw_beginner = self.make_workshop(
            title="Warsaw Beginner",
            city="Warsaw",
            skill_level=Event.BEGINNER,
            date=self.future_date(10),
        )
        self.gdansk_intermediate = self.make_workshop(
            title="Gdańsk Intermediate",
            city="Gdańsk",
            skill_level=Event.INTERMEDIATE,
            date=self.future_date(20),
        )
        self.warsaw_jam = self.make_jam(
            title="Warsaw Jam",
            city="Warsaw",
            date=self.future_date(15),
        )

    def test_filters_by_city_event_type_and_skill_level(self):
        response = self.client.get(
            "/events/",
            {
                "city": "Warsaw",
                "event_type": Event.WORKSHOP,
                "skill_level": Event.BEGINNER,
            },
        )

        self.assertContains(response, "Warsaw Beginner")
        self.assertNotContains(response, "Gdańsk Intermediate")
        self.assertNotContains(response, "Warsaw Jam")

    def test_filters_by_date_range(self):
        response = self.client.get(
            "/events/",
            {
                "date_from": self.future_date(18).isoformat(),
                "date_to": self.future_date(25).isoformat(),
            },
        )

        self.assertContains(response, "Gdańsk Intermediate")
        self.assertNotContains(response, "Warsaw Beginner")
        self.assertNotContains(response, "Warsaw Jam")

    def test_excludes_past_and_inactive_events_from_base_queryset(self):
        self.make_workshop(title="Old Event", date=self.past_date(5))
        self.make_workshop(title="Hidden Event", is_active=False)

        response = self.client.get("/events/")

        self.assertNotContains(response, "Old Event")
        self.assertNotContains(response, "Hidden Event")


class RegistrationIntegrationTests(IntegrationTestCase):
    def test_registration_persists_and_decrements_spots(self):
        event = self.make_workshop(capacity=5)
        Registration.objects.create(event=event, name="Existing", email="one@example.com")
        Registration.objects.create(event=event, name="Existing Two", email="two@example.com")

        response = self.client.post(
            f"/events/{event.pk}/register/",
            {"name": "New Person", "email": "new@example.com"},
            follow=True,
        )

        event.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(event.registration_count, 3)
        self.assertEqual(event.spots_remaining, 2)
        self.assertTrue(Registration.objects.filter(event=event, email="new@example.com").exists())
