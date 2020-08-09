from rest_framework import serializers

from payments.models import User, AccountCurrency


class UserSerializer(serializers.ModelSerializer):
    currency_type = serializers.ChoiceField(choices=AccountCurrency.CURRENCY_TYPE_CHOICES)
    balance_amount = serializers.IntegerField(min_value=0)

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
        user = User.objects.create_user(**validated_data)
        return user
