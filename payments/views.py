from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated

from payments.models import UserTransactionHistory, Currency
from payments.serializers import (UserRegistrationSerializer, UserTransactionHistorySerializer, CurrencySerializer,
                                  PaymentTransactionCreateSerializer)


class UserRegistrationAPIView(CreateAPIView):
    serializer_class = UserRegistrationSerializer


class UserTransactionsAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserTransactionHistorySerializer

    def get_queryset(self):
        return UserTransactionHistory.objects.filter(user=self.request.user)


class CurrencyApiView(ListAPIView):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer


class PaymentAPIView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentTransactionCreateSerializer
