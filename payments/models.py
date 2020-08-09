from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from common_mixins.model_mixins import AutoDateMixin


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('Email', unique=True)
    first_name = models.CharField('Имя', max_length=150, blank=True)
    last_name = models.CharField('Фамилия', max_length=150, blank=True)

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class AccountCurrency(AutoDateMixin, models.Model):
    EUR = 'eur'
    USD = 'usd'
    GPB = 'gpb'
    RUB = 'rub'
    BTC = 'btc'

    CURRENCY_TYPE_CHOICES = [
        (EUR, 'eur'),
        (USD, 'usd'),
        (GPB, 'gpb'),
        (RUB, 'rub'),
        (BTC, 'btc'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='Пользователь',
        related_name='currencies',
    )
    currency_type = models.CharField('Тип валюты', max_length=3, choices=CURRENCY_TYPE_CHOICES)
    balance_amount = models.IntegerField('Сумма баланса', default=0)

    class Meta:
        verbose_name = 'Валюта счета'
        verbose_name_plural = 'Валюты счетов'

    def __str__(self):
        return f'{self.user} ({self.currency_type})'


class PaymentTransaction(AutoDateMixin, models.Model):
    sender_account = models.ForeignKey(
        AccountCurrency,
        on_delete=models.PROTECT,
        verbose_name='Счет отправителя',
        related_name='sent_transactions',
    )
    recipient_account = models.ForeignKey(
        AccountCurrency,
        on_delete=models.PROTECT,
        verbose_name='Счет получателя',
        related_name='received_transactions',
    )
    transfer_amount = models.PositiveIntegerField('Сумма перевода')

    class Meta:
        verbose_name = 'Платежная транзакция'
        verbose_name_plural = 'Платежные транзакции'
