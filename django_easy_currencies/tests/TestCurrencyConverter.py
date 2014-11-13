from __future__ import unicode_literals
from decimal import Decimal
import os

from django.test.testcases import TestCase
from django.core.management import call_command
from django.test.utils import override_settings

from django_easy_currencies.utils import CurrencyConverter, CurrencyConverterException


SETTINGS = {
    'app_id': os.environ['EASY_CURRENCIES_APP_ID'],
    'currencies': (
        ('USD', 'Dollars'),
        ('EUR', 'Euro'),
        ('GBP', 'Pounds'),
    )
}


class TestCurrencyConverter(TestCase):
    def test_convert_raise_exception_if_rates_have_not_been_loaded(self):
        converter = CurrencyConverter('EUR')

        def bad():
            converter.convert(Decimal('49.9'), 'GBP')

        self.assertRaises(CurrencyConverterException, bad)

    @override_settings(EASY_CURRENCIES=SETTINGS)
    def test_convert_returns_same_value_if_target_and_source_currency_are_the_same(self):
        call_command('currencies', update=True)
        original_value = Decimal('49.9')
        converted_value = CurrencyConverter('USD').convert(original_value, 'USD')
        self.assertEqual(converted_value, original_value)
        converted_value = CurrencyConverter('EUR').convert(original_value, 'EUR')
        self.assertEqual(converted_value, original_value)
        converted_value = CurrencyConverter('GBP').convert(original_value, 'GBP')
        self.assertEqual(converted_value, original_value)

    @override_settings(EASY_CURRENCIES=SETTINGS)
    def test_convert_returns_higher_value_if_original_currency_is_stronger_than_target_one(self):
        call_command('currencies', update=True)
        original_value = Decimal('49.9')
        converted_value = CurrencyConverter('USD').convert(original_value, 'GBP')
        self.assertGreater(converted_value, original_value)
        converted_value = CurrencyConverter('USD').convert(original_value, 'EUR')
        self.assertGreater(converted_value, original_value)
        converted_value = CurrencyConverter('EUR').convert(original_value, 'GBP')
        self.assertGreater(converted_value, original_value)

    @override_settings(EASY_CURRENCIES=SETTINGS)
    def test_convert_returns_lower_value_if_original_currency_is_weaker_than_target_one(self):
        call_command('currencies', update=True)
        original_value = Decimal('49.9')
        converted_value = CurrencyConverter('GBP').convert(original_value, 'USD')
        self.assertLess(converted_value, original_value)
        converted_value = CurrencyConverter('GBP').convert(original_value, 'EUR')
        self.assertLess(converted_value, original_value)
        converted_value = CurrencyConverter('EUR').convert(original_value, 'USD')
        self.assertLess(converted_value, original_value)
