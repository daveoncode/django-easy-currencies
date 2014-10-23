from __future__ import unicode_literals
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models


class CurrencyRateManager(models.Manager):
    def get_rate_values(self, currency):
        records = self.select_related().values().filter(original_currency__code=currency)
        rates = {}
        for r in records:
            rates[r['target_currency']] = r['rate']
        return rates


class CurrencyRate(models.Model):
    class Meta:
        app_label = 'django_easy_currencies'
        db_table = 'django_easy_currencies_rate'
        verbose_name = 'Currency rate'
        verbose_name_plural = 'Currency rates'
        unique_together = (
            ('original_currency', 'target_currency'),
        )

    original_currency = models.ForeignKey('django_easy_currencies.Currency', related_name='rates')
    target_currency = models.CharField(max_length=3,
                                       validators=[MinLengthValidator(3), MaxLengthValidator(3)],
                                       db_index=True,
                                       editable=False)
    rate = models.DecimalField(max_digits=13, decimal_places=9) # (max: 9999.999999999)

    # custom manager
    objects = CurrencyRateManager()

    def __unicode__(self):
        return '{0}/{1}: {2}'.format(self.original_currency.code, self.target_currency, self.rate)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.target_currency:
            self.target_currency = self.target_currency.strip().upper()
        super(CurrencyRate, self).save(force_insert, force_update, using, update_fields)
