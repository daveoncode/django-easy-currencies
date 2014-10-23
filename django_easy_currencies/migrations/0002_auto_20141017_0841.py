# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_easy_currencies', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currencyrate',
            name='rate',
            field=models.DecimalField(max_digits=13, decimal_places=9),
        ),
    ]
