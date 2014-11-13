from __future__ import unicode_literals
from itertools import product
import os
from urllib2 import URLError
from decimal import Decimal

from django.test.testcases import TestCase
from django.test.utils import override_settings

from django_easy_currencies.management.commands.currencies import Command
from django_easy_currencies.models.Currency import Currency
from django_easy_currencies.models.CurrencyRate import CurrencyRate


VALID_SETTINGS = {
    'app_id': os.environ['EASY_CURRENCIES_APP_ID'],
    'currencies': (
        ('USD', 'Dollars'),
        ('EUR', 'Euro'),
        ('GBP', 'Pounds'),
    )
}


class OutputMock(object):
    @staticmethod
    def write(message):
        pass


class TestCurrenciesCommand(TestCase):
    def setUp(self):
        self.command = Command()
        self.command.stdout = OutputMock()
        self.command.stderr = OutputMock()

    @override_settings(EASY_CURRENCIES=None)
    def test_is_valid_config_returns_false_if_config_is_none(self):
        self.assertFalse(self.command.is_valid_config())

    @override_settings(EASY_CURRENCIES={})
    def test_is_valid_config_returns_false_if_config_is_empty(self):
        self.assertFalse(self.command.is_valid_config())

    @override_settings(EASY_CURRENCIES={'currencies': (('USD', 'Dollars'), ('EUR', 'Euro'))})
    def test_is_valid_config_returns_false_if_config_is_missing_app_id(self):
        self.assertFalse(self.command.is_valid_config())

    @override_settings(EASY_CURRENCIES={'app_id': '1234567890'})
    def test_is_valid_config_returns_false_if_config_is_missing_currencies(self):
        self.assertFalse(self.command.is_valid_config())

    @override_settings(EASY_CURRENCIES=VALID_SETTINGS)
    def test_is_valid_config_returns_true_if_currencies_and_app_id_are_defined(self):
        self.assertTrue(self.command.is_valid_config())

    @override_settings(EASY_CURRENCIES=VALID_SETTINGS)
    def test_get_currency_list_returns_expectd_list(self):
        expected = ['USD', 'EUR', 'GBP']
        self.assertEqual(self.command.get_currency_list(), expected)

    @override_settings(EASY_CURRENCIES=VALID_SETTINGS)
    def test_get_service_url_returns_expected_url(self):
        expected = 'http://openexchangerates.org/api/latest.json?app_id={}'.format(VALID_SETTINGS['app_id'])
        self.assertEqual(self.command.get_service_url(), expected)

    @override_settings(EASY_CURRENCIES=VALID_SETTINGS)
    def test_get_rates_info_returns_expected_list_of_tuples(self):
        currencies = self.command.get_currency_list()
        info = self.command.get_rates_info(self.command.get_service_url(), currencies)
        self.assertIsInstance(info, dict)
        self.assertIsInstance(info['rates'], list)
        self.assertEqual(len(info['rates']), len(currencies))
        for r in info['rates']:
            self.assertIsInstance(r, tuple)
            self.assertTrue(r[0] in currencies)
            self.assertIsInstance(r[1], Decimal)

    @override_settings(EASY_CURRENCIES={'currencies': (('USD', 'Dollars'), ('EUR', 'Euro')), 'app_id': 'invalid-code'})
    def test_get_rates_raise_exception_if_provided_app_id_is_invalid(self):
        def bad():
            self.command.get_rates_info(self.command.get_service_url(), self.command.get_currency_list())

        self.assertRaises(URLError, bad)

    @override_settings(EASY_CURRENCIES=VALID_SETTINGS)
    def test_create_or_update_currency_objects_creates_expected_records(self):
        self.assertEqual(Currency.objects.count(), 0)
        currencies = self.command.get_currency_list()
        self.command.create_or_update_currency_objects(currencies)
        self.assertEqual(Currency.objects.count(), len(currencies))

    @override_settings(EASY_CURRENCIES=VALID_SETTINGS)
    def test_create_or_update_currency_returns_dictionry_with_models(self):
        currencies = self.command.get_currency_list()
        res = self.command.create_or_update_currency_objects(currencies)
        self.assertIsInstance(res, dict)
        for c in currencies:
            self.assertTrue(c in res, '"{}" not in dictionary'.format(c))
            currency = res.get(c)
            self.assertIsInstance(currency, Currency)
            self.assertEqual(currency.code, c)

    @override_settings(EASY_CURRENCIES=VALID_SETTINGS)
    def test_create_or_update_usd_currency_rates_creates_expected_records(self):
        self.assertEqual(CurrencyRate.objects.count(), 0)
        currencies = self.command.get_currency_list()
        info = self.command.get_rates_info(self.command.get_service_url(), currencies)
        usd_currency, _ = Currency.objects.update_or_create(code='USD', defaults={'code': 'USD'})
        self.command.create_or_update_usd_currency_rates(info, usd_currency)
        records = CurrencyRate.objects.all()
        for record in records:
            self.assertIsInstance(record, CurrencyRate)
            self.assertEqual(record.original_currency, usd_currency)
            self.assertTrue(record.target_currency in currencies)
        self.assertEqual(len(records), len(currencies))

    @override_settings(EASY_CURRENCIES=VALID_SETTINGS)
    def test_create_or_update_usd_currency_rates_returns_dictionary_with_rate_values(self):
        self.assertEqual(CurrencyRate.objects.count(), 0)
        currencies = self.command.get_currency_list()
        info = self.command.get_rates_info(self.command.get_service_url(), currencies)
        usd_currency, _ = Currency.objects.update_or_create(code='USD', defaults={'code': 'USD'})
        res = self.command.create_or_update_usd_currency_rates(info, usd_currency)
        self.assertIsInstance(res, dict)
        for c in currencies:
            self.assertTrue(c in res, '"{}" not in dictionary'.format(c))
            self.assertIsInstance(res.get(c), Decimal)

    @override_settings(EASY_CURRENCIES=VALID_SETTINGS)
    def test_create_or_update_inverted_currency_rates_permutations_creates_expected_records(self):
        self.assertEqual(CurrencyRate.objects.count(), 0)
        currency_types = self.command.get_currency_list()
        info = self.command.get_rates_info(self.command.get_service_url(), currency_types)
        usd_currency, _ = Currency.objects.update_or_create(code='USD', defaults={'code': 'USD'})
        currencies = self.command.create_or_update_currency_objects(currency_types)
        usd_rates = self.command.create_or_update_usd_currency_rates(info, usd_currency)
        self.command.create_or_update_inverted_usd_currency_rates(currencies, usd_rates)
        self.command.create_or_update_inverted_currency_rates_permutations(currencies, currency_types, usd_rates)
        expected_records = len([p for p in product(currency_types, repeat=2)])
        self.assertEqual(CurrencyRate.objects.count(), expected_records)

    @override_settings(EASY_CURRENCIES=VALID_SETTINGS)
    def test_created_rates_have_rate_1_if_source_and_target_currency_are_equal(self):
        currency_types = self.command.get_currency_list()
        info = self.command.get_rates_info(self.command.get_service_url(), currency_types)
        usd_currency, _ = Currency.objects.update_or_create(code='USD', defaults={'code': 'USD'})
        currencies = self.command.create_or_update_currency_objects(currency_types)
        usd_rates = self.command.create_or_update_usd_currency_rates(info, usd_currency)
        self.command.create_or_update_inverted_usd_currency_rates(currencies, usd_rates)
        self.command.create_or_update_inverted_currency_rates_permutations(currencies, currency_types, usd_rates)
        for rate in CurrencyRate.objects.select_related().all():
            if rate.original_currency.code == rate.target_currency:
                self.assertEqual(rate.rate, 1)
