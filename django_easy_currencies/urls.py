from __future__ import unicode_literals
from django_easy_currencies.views.ChangeCurrencyView import ChangeCurrencyView
from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(
        regex=r'^change/$',
        view=ChangeCurrencyView.as_view(),
        name='change_currency'
    ),
)
