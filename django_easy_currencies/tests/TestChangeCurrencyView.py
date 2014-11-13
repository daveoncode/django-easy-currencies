from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.test.testcases import TestCase

from django.http.response import HttpResponseNotAllowed


class TestChangeCurrencyView(TestCase):
    def setUp(self):
        self.url = reverse('change_currency')

    def test_get_is_not_allowed(self):
        response = self.client.get(self.url)
        self.assertIsInstance(response, HttpResponseNotAllowed)

    def test_view_set_received_currency_in_session(self):
        self.assertIsNone(self.client.session.get('currency'))
        self.client.post(self.url, {'currency': 'EUR'})
        self.assertEqual(self.client.session.get('currency'), 'EUR')

    def test_view_set_usd_as_default_currency_if_currency_was_not_defined(self):
        self.assertIsNone(self.client.session.get('currency'))
        self.client.post(self.url, {})
        self.assertEqual(self.client.session.get('currency'), 'USD')
