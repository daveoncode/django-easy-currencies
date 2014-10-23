from __future__ import unicode_literals
from django.test.testcases import TestCase


class TestCurrencyContextProcessor(TestCase):
    def test_processor_sets_expected_variables_in_context(self):
        response = self.client.get('/')
        self.assertEqual(response.context['active_currency'], 'USD')
        self.assertIsInstance(response.context['currency_rates'], dict)
