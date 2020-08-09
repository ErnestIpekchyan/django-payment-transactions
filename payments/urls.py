from django.urls import path

from payments.views import UserRegistrationAPIView, UserTransactionsAPIView, CurrencyApiView

urlpatterns = [
    path('users/register/', UserRegistrationAPIView.as_view(), name='registration'),
    path('users/transactions/', UserTransactionsAPIView.as_view(), name='user_transactions'),
    path('currencies/', CurrencyApiView.as_view(), name='currencies'),
]
