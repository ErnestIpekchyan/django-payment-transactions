from django.urls import path

from payments.views import UserRegistrationAPIView, UserTransactionsAPIView, CurrencyApiView, PaymentAPIView

urlpatterns = [
    path('users/register/', UserRegistrationAPIView.as_view(), name='registration'),
    path('users/transactions/', UserTransactionsAPIView.as_view(), name='user_transactions'),
    path('users/payments/transfer/', PaymentAPIView.as_view(), name='payment_transfer'),
    path('currencies/', CurrencyApiView.as_view(), name='currencies'),
]
