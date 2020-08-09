from rest_framework.generics import CreateAPIView

from payments.serializers import UserRegistrationSerializer


class UserRegistrationAPIView(CreateAPIView):
    serializer_class = UserRegistrationSerializer
