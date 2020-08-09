from django.urls import reverse
from rest_framework.test import APITestCase

from payments.models import Currency, User, AccountCurrency


class UserRegistrationViewTest(APITestCase):

    def setUp(self):
        self.currency = Currency.objects.create(name='Евро', symbol='€', multiplicity=100, rate=1.151)
        self.url = reverse('registration')

    def test_registration(self):
        data = {
            'email': 'a@a.ru',
            'password': '1234',
            'first_name': 'Test',
            'currency_id': self.currency.id,
            'balance_amount': 20,
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 201)

        users = User.objects.filter(email='a@a.ru')
        self.assertTrue(users)
        account_currency = AccountCurrency.objects.filter(user=users.first(), currency=self.currency)
        self.assertTrue(account_currency)

    def test_registration_with_wrong_currency(self):
        pass
