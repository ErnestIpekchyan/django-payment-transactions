# Generated by Django 3.1 on 2020-08-09 17:42

from django.db import migrations


def add_currencies(apps, schema_editor):
    Currency = apps.get_model('payments', 'Currency')

    currencies = [
        Currency(name='Евро', symbol='€', multiplicity=100, rate=1.151),
        Currency(name='Доллар', symbol='$', multiplicity=100, rate=1.357),
        Currency(name='Фунт стерлингов', symbol='£', multiplicity=100, rate=1.04),
        Currency(name='Рубль', symbol='руб.', multiplicity=1, rate=1),
        Currency(name='Биткоин', symbol='₿', multiplicity=100, rate=0.00012),
    ]
    Currency.objects.bulk_create(currencies)


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0007_remove_accountcurrency_currency_type'),
    ]

    operations = [
        migrations.RunPython(add_currencies, migrations.RunPython.noop)
    ]
