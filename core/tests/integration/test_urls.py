from django.urls import resolve, reverse

from core import views

from ..base import UnitTestCase


class URLRoutingTests(UnitTestCase):
    def test_named_urls_resolve_to_expected_views(self):
        cases = [
            ("home", "/", views.home),
            ("events_list", "/events/", views.events_list),
            ("event_register", "/events/7/register/", views.event_register, {"event_id": 7}),
            ("jam_notify", "/events/7/notify/", views.jam_notify, {"event_id": 7}),
            ("polls_list", "/polls/", views.polls_list),
        ]
        for name, expected_path, view_func, *extra in cases:
            kwargs = extra[0] if extra else {}
            self.assertEqual(reverse(name, kwargs=kwargs), expected_path)
            match = resolve(expected_path)
            self.assertEqual(match.func, view_func)
