from rest_framework.generics import CreateAPIView, ListCreateAPIView

from payments.models import UserTransactionHistory
from payments.serializers import UserRegistrationSerializer, UserTransactionHistorySerializer


class UserRegistrationAPIView(CreateAPIView):
    serializer_class = UserRegistrationSerializer


class UserTransactionsAPIView(ListCreateAPIView):
    serializer_class = UserTransactionHistorySerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return UserTransactionHistory.objects.filter(user_id=user_id)
