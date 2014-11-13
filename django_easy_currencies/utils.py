from __future__ import unicode_literals
from decimal import Decimal

from django_easy_currencies.models.CurrencyRate import CurrencyRate


class CurrencyConverterException(Exception):
    pass


class CurrencyConverter(object):
    def __init__(self, target_currency):
        self.target_currency = target_currency
        self.currency_rates = CurrencyRate.objects.get_rate_values(target_currency)

    def convert(self, amount, current_currency):
        """
        Return the converted value of the given amount into the target currency.

        :param amount: Amount to convert.
        :param current_currency: Currency of the given amount.
        :return: :rtype:
        """
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        try:
            return amount / self.currency_rates[current_currency]
        except KeyError:
            raise CurrencyConverterException(
                'Unable to convert from "{}" to "{}", unavailable info. '
                'Have you run "currencies --update" command?'.format(current_currency, self.target_currency)
            )
