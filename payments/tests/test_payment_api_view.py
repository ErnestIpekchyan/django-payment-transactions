from decimal import Decimal

from django.urls import reverse
from rest_framework.test import APITestCase

from payments.models import Currency, User, AccountCurrency, UserTransactionHistory


class PaymentViewTest(APITestCase):

    def setUp(self):
        self.base_currency = Currency(name='Рубль', symbol='руб.', multiplicity=1, rate=1)
        self.url = reverse('payment_transfer')

    def register_user(self, email, currency, balance=0):
        data = {
            'email': email,
            'password': '1234',
            'first_name': 'Test',
            'currency_id': currency.id,
            'balance_amount': balance,
        }
        self.client.post(reverse('registration'), data=data)
        return User.objects.get(email=email)

    def test_payment_without_login(self):
        response = self.client.post(self.url)

        result_data = {'detail': 'Authentication credentials were not provided.'}
        self.assertEqual(response.json(), result_data)

    def test_payment_without_money(self):
        usd_currency = Currency.objects.create(name='Евро', symbol='€', multiplicity=100, rate=1.151)
        eur_currency = Currency.objects.create(name='Доллар', symbol='$', multiplicity=100, rate=1.357)
        sender = self.register_user('a@a.ru', usd_currency, 20)
        recipient = self.register_user('b@b.ru', eur_currency)
        sender_account = AccountCurrency.objects.get(user=sender, currency=usd_currency)
        recipient_account = AccountCurrency.objects.get(user=recipient, currency=eur_currency)

        self.client.force_login(sender)
        data = {
            'sender_account': sender_account.id,
            'recipient_account': recipient_account.id,
            'transfer_amount': 200,
        }
        response = self.client.post(self.url, data=data)
        result_data = {'non_field_errors': ['Недостаточно средств для перевода']}
        self.assertEqual(response.json(), result_data)

    def test_payment_with_negative_balance(self):
        usd_currency = Currency.objects.create(name='Евро', symbol='€', multiplicity=100, rate=1.151)
        eur_currency = Currency.objects.create(name='Доллар', symbol='$', multiplicity=100, rate=1.357)
        sender = self.register_user('a@a.ru', usd_currency)
        recipient = self.register_user('b@b.ru', eur_currency)
        sender_account = AccountCurrency.objects.get(user=sender, currency=usd_currency)
        recipient_account = AccountCurrency.objects.get(user=recipient, currency=eur_currency)

        self.client.force_login(sender)
        data = {
            'sender_account': sender_account.id,
            'recipient_account': recipient_account.id,
            'transfer_amount': 200,
        }
        response = self.client.post(self.url, data=data)
        result_data = {'non_field_errors': ['Баланс отрицательный. Невозможно выполнить перевод.']}
        self.assertEqual(response.json(), result_data)

    def test_payment_to_same_account(self):
        usd_currency = Currency.objects.create(name='Евро', symbol='€', multiplicity=100, rate=1.151)
        sender = self.register_user('a@a.ru', usd_currency, 1000)
        sender_account = AccountCurrency.objects.get(user=sender, currency=usd_currency)

        self.client.force_login(sender)
        data = {
            'sender_account': sender_account.id,
            'recipient_account': sender_account.id,
            'transfer_amount': 200,
        }
        response = self.client.post(self.url, data=data)
        result_data = {'non_field_errors': ['Нельзя совершить перевод на тот же счет']}
        self.assertEqual(response.json(), result_data)

    def test_payment_from_wrong_account(self):
        usd_currency = Currency.objects.create(name='Евро', symbol='€', multiplicity=100, rate=1.151)
        eur_currency = Currency.objects.create(name='Доллар', symbol='$', multiplicity=100, rate=1.357)
        sender = self.register_user('a@a.ru', usd_currency)
        recipient = self.register_user('b@b.ru', eur_currency, 1000)
        sender_account = AccountCurrency.objects.get(user=sender, currency=usd_currency)
        recipient_account = AccountCurrency.objects.get(user=recipient, currency=eur_currency)

        self.client.force_login(sender)
        data = {
            'sender_account': recipient_account.id,
            'recipient_account': sender_account.id,
            'transfer_amount': 200,
        }
        response = self.client.post(self.url, data=data)
        result_data = {'non_field_errors': ['Счет не принадлежит текущему пользователю']}
        self.assertEqual(response.json(), result_data)

    def test_payment_from_usd_to_eur(self):
        usd_currency = Currency.objects.create(name='Евро', symbol='€', multiplicity=100, rate=1.151)
        eur_currency = Currency.objects.create(name='Доллар', symbol='$', multiplicity=100, rate=1.357)
        sender = self.register_user('a@a.ru', usd_currency, 1000)
        recipient = self.register_user('b@b.ru', eur_currency)
        sender_account = AccountCurrency.objects.get(user=sender, currency=usd_currency)
        recipient_account = AccountCurrency.objects.get(user=recipient, currency=eur_currency)

        self.client.force_login(sender)
        data = {
            'sender_account': sender_account.id,
            'recipient_account': recipient_account.id,
            'transfer_amount': 200,
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 201)

        debit_payment = UserTransactionHistory.objects.filter(
            user=sender, payment_type=UserTransactionHistory.DEBIT,
        )
        add_payment = UserTransactionHistory.objects.filter(
            user=recipient, payment_type=UserTransactionHistory.ADD,
        )
        self.assertTrue(debit_payment)
        self.assertTrue(add_payment)
        self.assertEqual(debit_payment.last().transfer_amount, 200)
        self.assertEqual(add_payment.last().transfer_amount, Decimal('235.79'))

        sender_account.refresh_from_db()
        recipient_account.refresh_from_db()
        self.assertEqual(sender_account.balance_amount, Decimal('800'))
        self.assertEqual(recipient_account.balance_amount, Decimal('235.79'))
