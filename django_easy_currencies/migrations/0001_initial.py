# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):
    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('code', models.CharField(primary_key=True, serialize=False, max_length=3,
                                          validators=[django.core.validators.MinLengthValidator(3),
                                                      django.core.validators.MaxLengthValidator(3)],
                                          help_text='Currency code in ISO 4217 format ($ == USD)', db_index=True)),
            ],
            options={
                'db_table': 'django_easy_currencies_currency',
                'verbose_name': 'Currency',
                'verbose_name_plural': 'Currencies',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CurrencyRate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('target_currency', models.CharField(db_index=True, max_length=3, editable=False,
                                                     validators=[django.core.validators.MinLengthValidator(3),
                                                                 django.core.validators.MaxLengthValidator(3)])),
                ('rate', models.FloatField()),
                ('original_currency', models.ForeignKey(related_name='rates', to='django_easy_currencies.Currency')),
            ],
            options={
                'db_table': 'django_easy_currencies_rate',
                'verbose_name': 'Currency rate',
                'verbose_name_plural': 'Currency rates',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='currencyrate',
            unique_together=set([('original_currency', 'target_currency')]),
        ),
    ]
