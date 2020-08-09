from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from common_mixins.model_mixins import AutoDateMixin
from payments.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('Email', unique=True)
    first_name = models.CharField('Имя', max_length=150, blank=True)
    last_name = models.CharField('Фамилия', max_length=150, blank=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class Currency(AutoDateMixin, models.Model):
    EUR = '€'
    USD = '$'
    GPB = '£'
    RUB = 'руб.'
    BTC = '₿'

    SYMBOL_CHOICES = [
        (EUR, '€'),
        (USD, '$'),
        (GPB, '£'),
        (RUB, 'руб.'),
        (BTC, '₿'),
    ]

    name = models.CharField('Название', max_length=30)
    symbol = models.CharField('Символ', max_length=5, choices=SYMBOL_CHOICES)
    multiplicity = models.PositiveIntegerField('Кратность')
    rate = models.FloatField('Курс')

    class Meta:
        verbose_name = 'Валюта'
        verbose_name_plural = 'Валюты'

    def __str__(self):
        return self.name


class AccountCurrency(AutoDateMixin, models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='Пользователь',
        related_name='currencies',
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        verbose_name='Валюта',
        related_name='accounts',
    )
    balance_amount = models.DecimalField(
        'Сумма баланса',
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    class Meta:
        verbose_name = 'Валюта счета'
        verbose_name_plural = 'Валюты счетов'

    def __str__(self):
        return f'{self.user} ({self.currency.name})'


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

    class Meta:
        verbose_name = 'Платежная транзакция'
        verbose_name_plural = 'Платежные транзакции'

    def __str__(self):
        return f'From {self.sender_account} to {self.recipient_account} - {self.dt_created}'


class UserTransactionHistory(AutoDateMixin, models.Model):
    ADD = 'add'
    DEBIT = 'debit'

    PAYMENT_TYPE_CHOICES = [
        (ADD, 'Пополнение'),
        (DEBIT, 'Списание'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='Пользователь',
        related_name='transactions',
    )
    payment = models.ForeignKey(
        PaymentTransaction,
        on_delete=models.PROTECT,
        verbose_name='Платежная транзакция',
        related_name='participants',
    )
    payment_type = models.CharField('Тип перевода', max_length=5, choices=PAYMENT_TYPE_CHOICES)
    transfer_amount = models.DecimalField('Сумма перевода', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'История операций'
        verbose_name_plural = 'История операций'

    def __str__(self):
        return f'{self.user} ({self.payment_type})'
