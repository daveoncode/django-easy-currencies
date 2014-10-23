# Django Easy Currencies

Simple app to manage currencies convertion in Django using [openexchangerates.org](https://openexchangerates.org) service.

The app will automatically invokes the service and in a **single HTTP call** it will creates all the necessary conversion rates permutations offline **by "bypassing" the free account limitation which limits the source currency to USD** using simple math alghoritms and the excellent Python's `itertools` utilities (so this is 100% legal!).

---

## Quick start

### Installation

1. Get an app key from [openexchangerates.org](https://openexchangerates.org) (you don't need to pay, the basic free account will be enough)

2. Add "django_easy_currencies" to your `INSTALLED_APPS` setting like this:

   ```
   INSTALLED_APPS = (
      ...
      'django_easy_currencies',
   )
   ```

3. Configure the app by providing your app id and the currencies you want to use like this:

   ```
   EASY_CURRENCIES = {
     'currencies': (
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('AUD', 'Australian Dollar'),
        ('CAD', 'Canadian Dollar'),
        ('CHF', 'Swiss Franc'),
        ('JPY', 'Japanese Yen'),
      ),
     'app_id': os.environ['EASY_CURRENCIES_APP_ID']
   } 
   ```
   **Just a note**: *An environment variable holding your app id is a best practice but is not mandatory, you can define it inline in your settings.py*

4. Include the "**django_easy_currencies**" URLconf in your project urls.py like this:

   ```
   url(r'^currency/', include('django_easy_currencies.urls')),
   ```

5. Add the "**django_easy_currencies**" context processor to your existent processors like this:

   ```
   from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as BASE_CONTEXT_PROCESSORS

   TEMPLATE_CONTEXT_PROCESSORS = BASE_CONTEXT_PROCESSORS + (
      'django_easy_currencies.context_processors.currency',
   )
   ```

6. Run `python manage.py migrate` to create the app models.

7. Run the custom management command `python manage.py currencies --update` to save currency rates in your database. 
*You should run this command at least once a day in order to have updated rates (automatization of this step is up to you)*

8. (Optional) Run `python manage.py currencies --list` to see the loaded currency rates

### Change active currency

The default currency automatically activated by the context porcessor is "**USD**".
To change it "**django_easy_currencies**" provides a custom tag which prints a combo with all the available currencies and calls `ChangeCurrencyView` as soon the user select a new option.
To use the tag you just need to:

1. Load the tag library: 

   `{% load currencies %}`

2. Use the tag:

   `{% currencies_combo %}`



### Display localized currencies in templates

1. Load the tag library: 

   `{% load currencies %}`
2. Use the custom tag to display the converted price: 

   `{% local_currency original_price original_currency %}`
   
   The tag will convert the `original_price` using `original_currency` into the currenct active currency (which is available in template context as "`active_currency`"). And formatting it with the right currency symbol.
   
   So, supposing you are going to print a localized book price which originally is **39.50 USD **and the active currency is **EUR**, the result will be something like: **€ 31,26**.
   And in the template it will looks like:
   
   `{% local_currency book.price 'USD' %}` 
   
   or 
   
   `{% local_currency book.price book.original_currency %}`
   
   It's also possible to skip number formatting by passing `False` as the third tag argument:
   
   `{% local_currency book.price 'USD' False %}`
   
   In this way the output will be simply: **31.26**
   
    