from __future__ import unicode_literals
from optparse import make_option
from urllib2 import URLError
import urllib2
import json
from itertools import product
from decimal import Decimal

from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand
from django.conf import settings

from django_easy_currencies.models.Currency import Currency
from django_easy_currencies.models.CurrencyRate import CurrencyRate


class Command(BaseCommand):
    help = 'Updates or list rates of supported currencies.'
    base_service_url = 'http://openexchangerates.org/api/latest.json?app_id={0}'
    option_list = BaseCommand.option_list + (
        make_option('--update',
                    action='store_true',
                    dest='update',
                    default=False,
                    help='Update currency rates'),
        make_option('--list',
                    action='store_true',
                    dest='list',
                    default=False,
                    help='List current currency rates'),
    )

    @staticmethod
    def is_valid_config():
        c = getattr(settings, 'EASY_CURRENCIES', None)
        return isinstance(c, dict) and isinstance(c.get('currencies'), (list, tuple)) and bool(c.get('app_id'))

    def get_rates_info(self, url, currencies):
        """
        Makes an http call to the rates service and returns a python dictionary.

        :param url:
        :param currencies:
        :return: :rtype: :raise exception:
        """
        try:
            self.stdout.write('Calling service: {0}'.format(url))
            response = urllib2.urlopen(url)
            if not response:
                raise Exception('Invalid response')
            info = json.loads(response.read(), parse_float=Decimal, parse_int=Decimal)
            info['rates'] = [(k, v) for k, v in info['rates'].items() if k in currencies]
            return info
        except URLError as url_error:
            self.stderr.write('Unable to connect to service {0}: {1}'.format(url, url_error))
            raise url_error
        except Exception as exception:
            self.stderr.write('Unable to retrieve ratings info: {0}'.format(exception))
            raise exception

    def create_or_update_currency_objects(self, currency_types):
        """
        Creates records for Currency objects if not already defined and return them in a dictionary for later access.

        :param currency_types:
        :return: :rtype:
        """
        self.stdout.write('Updating currency objects...')
        currencies = {}
        for c in currency_types:
            self.stdout.write('Updating currency: {0}'.format(c))
            currency, created = Currency.objects.update_or_create(code=c, defaults={'code': c})
            currencies[c] = currency
        return currencies

    def create_or_update_usd_currency_rates(self, info, usd_currency):
        """
        Returns a dictionary containing CurrencyRate objects related to USD currency.

        :param info:
        :param usd_currency:
        :return: :rtype:
        """
        rates = {}
        for rate_code, rate_value in info['rates']:
            self.stdout.write('Updating rates for currency: {0}'.format(rate_code))
            rate_obj, _ = CurrencyRate.objects.update_or_create(original_currency=usd_currency,
                                                                target_currency=rate_code,
                                                                defaults={'rate': rate_value})
            rates[rate_code] = rate_obj.rate
        return rates

    def create_or_update_inverted_usd_currency_rates(self, currencies, usd_rates):
        """
        Save the inverted rates of USD rates (ie: from USD/EUR, USD/GBP... -> EUR/USD, GBP/USD...)

        :param currencies:
        :param usd_rates:
        """
        self.stdout.write('Updating reversed rates for USD currency...')
        for code, currency_obj in currencies.items():
            self.stdout.write('Updating rate {0}/USD'.format(code))
            rate_value = Decimal('1') if code == 'USD' else Decimal('1') / usd_rates[code]
            CurrencyRate.objects.update_or_create(original_currency=currency_obj,
                                                  target_currency='USD',
                                                  defaults={'rate': rate_value})

    def create_or_update_inverted_currency_rates_permutations(self, currencies, currency_types, usd_rates):
        """
        Saves recursively all the possible currency rates.

        :param currencies:
        :param currency_types:
        :param usd_rates:
        """
        self.stdout.write('Updating reversed rates permutations...')
        for p in [x for x in product(currency_types, repeat=2)]:
            from_currency, to_currency = p
            self.stdout.write('Updating rate {0}/{1}'.format(from_currency, to_currency))
            if from_currency == to_currency:
                rate_value = Decimal('1')
            else:
                rate_value = Decimal('1') / usd_rates[from_currency] / usd_rates[to_currency]
            CurrencyRate.objects.update_or_create(original_currency=currencies[from_currency],
                                                  target_currency=to_currency,
                                                  defaults={'rate': rate_value})

    @staticmethod
    def get_currency_list():
        """
        Returns a list of supported currencies without the USD (which is the default one)

        :return: :rtype:
        """
        return [c[0] for c in settings.EASY_CURRENCIES['currencies']]

    def get_service_url(self):
        """
        Returns the configured service url to call.

        :return: :rtype:
        """
        return self.base_service_url.format(settings.EASY_CURRENCIES['app_id'])

    def update_currency_rates(self):
        """
        Updates currencies/rates by following these steps:
        1. Calls the remote service and retrieve the json response converted into a python dictionary
        2. Retrieve base USD Currency (creates it if does not exist)
        3. Retrieve extra USD currencies supported by configuration (creates them if not defined)
        4. Creates/updates USD rates
        5. Creates/updates all other supported currency rates recursively

        """
        self.stdout.write('Updating currency rates...')
        currency_types = self.get_currency_list()
        info = self.get_rates_info(self.get_service_url(), currency_types)
        try:
            usd_currency, _ = Currency.objects.update_or_create(code='USD', defaults={'code': 'USD'})
            currencies = self.create_or_update_currency_objects(currency_types)
            usd_rates = self.create_or_update_usd_currency_rates(info, usd_currency)
            self.create_or_update_inverted_usd_currency_rates(currencies, usd_rates)
            self.create_or_update_inverted_currency_rates_permutations(currencies, currency_types, usd_rates)
            self.stdout.write('Currency rates have been updated, run command with "--list" to see current status.')
        except Exception as e:
            self.stderr.write('An error occurred while updating currency rates: {0}'.format(e))

    def list_current_currency_rates(self):
        if CurrencyRate.objects.count() < 1:
            self.stdout.write('No currency rates available... run the command using --update to add new rates')
        else:
            for r in CurrencyRate.objects.select_related().all():
                self.stdout.write(unicode(r))

    def handle(self, *args, **options):
        if not self.is_valid_config():
            raise ImproperlyConfigured('EASY_CURRENCIES configuration is invalid')
        if options['update']:
            self.update_currency_rates()
        elif options['list']:
            self.list_current_currency_rates()
