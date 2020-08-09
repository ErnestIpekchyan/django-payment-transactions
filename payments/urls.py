from django.urls import path

from payments.views import UserRegistrationAPIView

urlpatterns = [
    path('users/register/', UserRegistrationAPIView.as_view(), name='registration'),
]
