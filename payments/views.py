from rest_framework.generics import CreateAPIView

from payments.serializers import UserSerializer


class UserRegistrationAPIView(CreateAPIView):
    serializer_class = UserSerializer
