from django.db import transaction
from rest_framework import serializers

from payments.models import User, AccountCurrency, UserTransactionHistory, PaymentTransaction


class UserRegistrationSerializer(serializers.ModelSerializer):
    currency_type = serializers.ChoiceField(choices=AccountCurrency.CURRENCY_TYPE_CHOICES, write_only=True)
    balance_amount = serializers.IntegerField(min_value=0, write_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'password',
            'first_name',
            'last_name',
            'currency_type',
            'balance_amount',
        ]

    def create(self, validated_data):
        currency_type = validated_data.pop('currency_type')
        balance_amount = validated_data.pop('balance_amount')

        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
            AccountCurrency.objects.create(
                user=user,
                currency_type=currency_type,
                balance_amount=balance_amount,
            )
        return user


class UserTransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTransactionHistory
        fields = ['id', 'payment', 'payment_type']


class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = ['id', 'recipient_account', 'transfer_amount']
