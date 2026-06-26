from core.models import Subscriber

from ..base import AcceptanceTestCase, TransactionAcceptanceTestCase


class SubscribeAcceptanceTests(AcceptanceTestCase):
    def test_home_newsletter_subscription_creates_subscriber(self):
        response = self.client.post(
            '/',
            {
                'form_type': 'subscribe',
                'email': 'news@example.com',
                'city_interest': 'Warsaw',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        subscriber = Subscriber.objects.get(email='news@example.com')
        self.assertEqual(subscriber.city_interest, 'Warsaw')
        self.assert_page_contains(response, 'on the list')

    def test_jam_notify_creates_subscriber_with_city_interest(self):
        event = self.make_jam(city='Kraków')

        response = self.client.post(
            f'/events/{event.pk}/notify/',
            {'email': 'jamfan@example.com'},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        subscriber = Subscriber.objects.get(email='jamfan@example.com')
        self.assertEqual(subscriber.city_interest, 'Kraków')
        self.assert_page_contains(response, 'notify you of any changes')


class SubscribeDuplicateTests(TransactionAcceptanceTestCase):
    def test_duplicate_newsletter_subscription_shows_info_message(self):
        Subscriber.objects.create(email='repeat@example.com', city_interest='Kraków')

        response = self.client.post(
            '/',
            {
                'form_type': 'subscribe',
                'email': 'repeat@example.com',
                'city_interest': 'Gdańsk',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Subscriber.objects.filter(email='repeat@example.com').count(), 1)
        self.assert_page_contains(response, 'already subscribed')

    def test_duplicate_jam_notify_shows_info_message(self):
        event = self.make_jam(city='Kraków')
        Subscriber.objects.create(email='repeat@example.com', city_interest='Kraków')

        response = self.client.post(
            f'/events/{event.pk}/notify/',
            {'email': 'repeat@example.com'},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Subscriber.objects.filter(email='repeat@example.com').count(), 1)
        self.assert_page_contains(response, 'already on our list')