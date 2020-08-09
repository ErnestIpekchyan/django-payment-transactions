from decimal import Decimal

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from payments.models import User, AccountCurrency, UserTransactionHistory, PaymentTransaction, Currency


class UserRegistrationSerializer(serializers.ModelSerializer):
    currency_id = serializers.IntegerField(min_value=0, write_only=True)
    balance_amount = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True, min_value=0)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'password',
            'first_name',
            'last_name',
            'balance_amount',
            'currency_id',
        ]

    def create(self, validated_data):
        currency_id = validated_data.pop('currency_id')
        balance_amount = validated_data.pop('balance_amount')

        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
            AccountCurrency.objects.create(
                user=user,
                currency_id=currency_id,
                balance_amount=balance_amount,
            )
        return user

    def validate_currency_id(self, currency_id):
        currency = Currency.objects.filter(id=currency_id)
        if not currency.exists():
            raise ValidationError('Такой валюты не существует')
        return currency_id


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'name', 'symbol', 'multiplicity', 'rate']


class AccountCurrencySerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email')
    currency = serializers.CharField(source='currency.name')

    class Meta:
        model = AccountCurrency
        fields = ['id', 'user_email', 'currency']


class PaymentTransactionSerializer(serializers.ModelSerializer):
    sender_account = AccountCurrencySerializer()
    recipient_account = AccountCurrencySerializer()

    class Meta:
        model = PaymentTransaction
        fields = ['id', 'sender_account', 'recipient_account']


class UserTransactionHistorySerializer(serializers.ModelSerializer):
    payment = PaymentTransactionSerializer()

    class Meta:
        model = UserTransactionHistory
        fields = ['id', 'payment', 'payment_type', 'transfer_amount']


class PaymentTransactionCreateSerializer(serializers.ModelSerializer):
    transfer_amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    converted_sum = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0, read_only=True)

    class Meta:
        model = PaymentTransaction
        fields = ['id', 'sender_account', 'recipient_account', 'transfer_amount', 'converted_sum']

    def create(self, validated_data):
        sender_account = validated_data['sender_account']
        recipient_account = validated_data['recipient_account']
        transfer_amount = validated_data['transfer_amount']
        converted_sum = self.convert_currency()

        with transaction.atomic():
            payment = PaymentTransaction.objects.create(
                sender_account=validated_data['sender_account'],
                recipient_account=validated_data['recipient_account'],
            )
            UserTransactionHistory.objects.create(
                user=sender_account.user,
                payment=payment,
                payment_type=UserTransactionHistory.DEBIT,
                transfer_amount=transfer_amount,
            )
            UserTransactionHistory.objects.create(
                user=recipient_account.user,
                payment=payment,
                payment_type=UserTransactionHistory.ADD,
                transfer_amount=converted_sum,
            )

            sender_account.balance_amount -= transfer_amount
            sender_account.save(update_fields=['balance_amount'])
            recipient_account.balance_amount += converted_sum
            recipient_account.save(update_fields=['balance_amount'])

        result_data = validated_data.copy()
        result_data['converted_sum'] = converted_sum
        return result_data

    def validate(self, attrs):
        request = self.context['request']

        sender_account = attrs.get('sender_account')
        recipient_account = attrs.get('recipient_account')
        transfer_amount = attrs.get('transfer_amount')

        if sender_account.balance_amount <= 0:
            raise ValidationError('Баланс отрицательный. Невозможно выполнить перевод.')
        if sender_account.balance_amount < transfer_amount:
            raise ValidationError('Недостаточно средств для перевода')
        if sender_account == recipient_account:
            raise ValidationError('Нельзя совершить перевод на тот же счет')
        if sender_account.user != request.user:
            raise ValidationError('Счет не принадлежит текущему пользователю')
        return attrs

    def convert_currency(self):
        sender_account = self.validated_data['sender_account']
        recipient_account = self.validated_data['recipient_account']
        transfer_amount = self.validated_data['transfer_amount']

        if sender_account.currency == recipient_account.currency:
            return transfer_amount

        base_currency = Currency.objects.get(multiplicity=1)
        if sender_account.currency == base_currency:
            return self.convert_from_base_currency()
        if recipient_account.currency == base_currency:
            return self.convert_to_base_currency()
        return self.convert_between_currencies()

    def convert_from_base_currency(self):
        recipient_account = self.validated_data['recipient_account']
        transfer_amount = self.validated_data['transfer_amount']

        recipient_currency_rate = Decimal(recipient_account.currency.rate)
        return recipient_currency_rate * transfer_amount / recipient_account.currency.multiplicity

    def convert_to_base_currency(self):
        sender_account = self.validated_data['sender_account']
        transfer_amount = self.validated_data['transfer_amount']

        sender_currency_rate = Decimal(sender_account.currency.rate)
        return transfer_amount * sender_account.currency.multiplicity / sender_currency_rate

    def convert_between_currencies(self):
        sender_account = self.validated_data['sender_account']
        recipient_account = self.validated_data['recipient_account']
        transfer_amount = self.validated_data['transfer_amount']

        sender_currency_rate = Decimal(sender_account.currency.rate)
        recipient_currency_rate = Decimal(recipient_account.currency.rate)
        dividend = transfer_amount * sender_account.currency.multiplicity * recipient_currency_rate
        divider = recipient_account.currency.multiplicity * sender_currency_rate
        return dividend / divider
