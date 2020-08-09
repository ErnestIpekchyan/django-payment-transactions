from django.urls import path

from payments.views import UserRegistrationAPIView, UserTransactionsAPIView

urlpatterns = [
    path('users/register/', UserRegistrationAPIView.as_view(), name='registration'),
    path('transactions/', UserTransactionsAPIView.as_view(), name='user_transactions'),
]
