from __future__ import unicode_literals
from django_easy_currencies.models.CurrencyRate import CurrencyRate


def currency(request):
    """
    Add active_currency and currency_rates rates into context_data.

    :param request:
    :return: :rtype:
    """
    cur = request.session.get('currency', 'USD')
    rates = CurrencyRate.objects.get_rate_values(cur)  # todo: handle caching
    return {
        'active_currency': cur,
        'currency_rates': rates
    }
