from __future__ import unicode_literals
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models


class Currency(models.Model):
    class Meta:
        app_label = 'django_easy_currencies'
        db_table = 'django_easy_currencies_currency'
        verbose_name = 'Currency'
        verbose_name_plural = 'Currencies'

    code = models.CharField(max_length=3,
                            validators=[MinLengthValidator(3), MaxLengthValidator(3)],
                            help_text='Currency code in ISO 4217 format ($ == USD)',
                            db_index=True,
                            primary_key=True)

    def __unicode__(self):
        return self.code

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.code:
            self.code = self.code.strip().upper()
        super(Currency, self).save(force_insert, force_update, using, update_fields)
