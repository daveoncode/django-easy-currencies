from __future__ import unicode_literals
from django import template
from django.conf import settings
from babel.numbers import format_currency
from django.template.base import TemplateSyntaxError
from django.utils.functional import cached_property

register = template.Library()


class CurrencyConversionNode(template.Node):
    def __init__(self, price, source_currency, formatted=True):
        """

        :param price: Price to convert.
        :param source_currency: Original curreny of the price to convert.
        :param formatted: True to return a locale-formatted string, False to return a Decimal instance.
        """
        self.original_price_var = price
        self.source_currency_var = source_currency
        self.formatted = True if str(formatted) == 'True' else False  # ("formatted" is received as string from tag)
        self.context = None

    def resolve_var(self, var):
        """
        Returns the value of the given variable using existent template context.

        :param var:
        :return: :rtype:
        """
        return template.Variable(var).resolve(self.context)

    @cached_property
    def active_currency(self):
        return self.resolve_var('active_currency')  # (inject into template by context processor)

    @cached_property
    def currency_rates(self):
        return self.resolve_var('currency_rates')  # (inject into template by context processor)

    def get_converted_price(self):
        source_currency = self.resolve_var(self.source_currency_var)
        return self.resolve_var(self.original_price_var) / self.currency_rates[source_currency]

    def render(self, context):
        self.context = context
        converted_price = self.get_converted_price()
        if self.formatted:
            return format_currency(converted_price, self.active_currency)
        return unicode(converted_price)


@register.tag
def local_currency(parser, token):
    """
    Returns a price converted to the current active currency from the original currency.

    :param parser:
    :param token:
    :return: :rtype: :raise TemplateSyntaxError:
    """
    params = token.split_contents()[1:]
    count = len(params)
    if count < 2:
        msg = 'Invalid number of arguments ({0}), must be at least 2: price, currency.'
        raise TemplateSyntaxError(msg.format(count))
    return CurrencyConversionNode(*params)


@register.inclusion_tag('currencies_combo.html', takes_context=True)
def currencies_combo(context):
    """
    Render a simple combo that lists available currencies and allows to swith among them.

    :param context:
    :return: :rtype:
    """
    context.update({'currencies': settings.EASY_CURRENCIES['currencies']})
    return context
