# django-payment-transactions
Django project for making payment transfers between accounts

# Requirements
- Python 3.8.2
- Django 3.0.8
- djangorestframework 3.11.0

# Installation
- Clone this repository:

```
cd
git clone https://github.com/ErnestIpekchyan/django-payment-transactions.git
```

- Install requirements:

```
pip install -r requirements.txt
```

- Add `.env` file into project directory and override default settings if needed.  
For example:
```.env
DEBUG=True
SECRET_KEY="****"
```

- Run server and use API

# Usage

- URL for register user (`POST` request):

```
/users/register/
```
Параметры запроса:
```
{
  "email': "a@a.ru",
  "password": "1234",
  "first_name": "Test",
  "currency_id": <id_валюты>, # из модели Currency
  "balance_amount": 20 # сумма начального баланса на счете
}
```
В случае успешной регистрации возвращает 201 статус.

- URL for get user transactions (`GET` request):

```
/users/transactions/
```

- URL for transfer money between accounts (`POST` request):

```
/users/payments/transfer/
```

Параметры запроса:
```
{
  "sender_account": <id_счета_отправителя>, # из модели AccountCurrency (счет создается после регистрации юзера)
  "recipient_account": <id_счета_получателя>, # из модели AccountCurrency
  "transfer_amount": 200
}
```
В случае успешного перевода возвращает 201 статус.

# Testing
Run tests with the following command:

```
python manage.py test --nomigrations
```
