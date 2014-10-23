from __future__ import unicode_literals
from django.http.response import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic.base import View


class ChangeCurrencyView(View):
    @method_decorator(require_POST)
    def dispatch(self, request, *args, **kwargs):
        """
        Sets currency in session then redirects to the previous page.

        :param request:
        :param args:
        :param kwargs:
        :return: :rtype:
        """
        request.session['currency'] = request.POST.get('currency', 'USD')
        origin = self.request.META.get('HTTP_REFERER', '/')
        return HttpResponseRedirect(origin)
