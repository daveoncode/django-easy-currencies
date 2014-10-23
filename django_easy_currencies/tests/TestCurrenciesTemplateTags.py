from __future__ import unicode_literals
from decimal import Decimal

from django.test.testcases import TestCase
from django.template import Template, Context


class TestCurrenciesTemplateTags(TestCase):
    def test_local_currency_converts_original_price(self):
        template = Template(
            '{% load currencies %}'
            '{% local_currency original_price original_currency False %}'
        )
        price = Decimal('59.90')
        rate = Decimal('1.277421448')
        context = Context({
            'original_price': price,
            'original_currency': 'USD',
            'active_currency': 'EUR',
            'currency_rates': {'USD': rate}
        })
        output = template.render(context).strip()
        self.assertEqual(output, str(price / rate))
        self.assertTrue(Decimal(output) < price)

    def test_local_currency_formats_currency_with_expected_symbol(self):
        template = Template(
            '{% load currencies %}'
            '{% local_currency original_price original_currency %}'
        )
        context = Context({
            'original_price': Decimal('59.90'),
            'original_currency': 'USD',
            'active_currency': 'EUR',
            'currency_rates': {'USD': Decimal('1.277421448')}
        })
        output = template.render(context).strip()
        self.assertTrue(output.startswith('\u20AC'))
