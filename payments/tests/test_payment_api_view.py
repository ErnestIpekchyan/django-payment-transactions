from django.urls import reverse
from rest_framework.test import APITestCase


class PaymentViewTest(APITestCase):

    def setUp(self):
        self.url = reverse('payment_transfer')

    def test_payment_without_login(self):
        response = self.client.post(self.url)

        result_data = {'detail': 'Authentication credentials were not provided.'}
        self.assertEqual(response.json(), result_data)
