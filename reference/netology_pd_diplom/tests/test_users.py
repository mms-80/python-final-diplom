import pytest
from django.urls import reverse
from rest_framework import status
from backend.models import User, ConfirmEmailToken, Contact
from tests.conftest import NEW_USER_PROFILE_INFO


@pytest.mark.django_db
class TestUser:

    # регистрация пользователя
    def test_registration(self, api_client):
        url = reverse('backend:user-register')
        # сформировать данные пользователя
        test_user = {'email': 'sds-diplom-24@mail.ru', **NEW_USER_PROFILE_INFO}
        # отправить запроса на регистрацию
        resp = api_client.post(url, test_user)
        # проверить что регистрация прошла успешно
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert resp_json.get('Status') == True
        # проверить наличие пользователя в БД
        created_user = User.objects.get(email=test_user['email'])
        assert created_user
        # проверить что все поля заполнены верно
        test_user.pop('password')
        for test_user_field in test_user.keys():
            assert getattr(created_user, test_user_field) == test_user[test_user_field]


    # сброс пароля
    def test_password_reset(self, api_client, user_buyer):
        url = reverse('backend:password-reset')
        resp = api_client.post(
            url,
            data={
                'email': user_buyer.email
            }
        )
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert {'status', } <= set(resp_json.keys())
        assert resp_json.get('status') == 'OK'


    # получить список контактов пользователя
    def test_user_contact_get(self, api_client, user_buyer_token, request, user_buyer, contact_factory):
        url = reverse('backend:user-contact')
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + user_buyer_token.key)
        contacts = contact_factory(user=user_buyer, _quantity=3)
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert resp_json
        assert len(resp_json) == len(contacts)
        assert {'id', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'phone'} <= set(resp_json[0].keys())


    # создать контакт пользователя
    def test_user_contact_post(self, api_client, user_buyer_token, user_buyer):
        url = reverse('backend:user-contact')
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + user_buyer_token.key)
        resp = api_client.post(
            url, 
            data={
                'city': 'Москва',
                'street': 'ул. Строителей',
                'house': '25',
                'structure': '1',
                'building': '1',
                'apartment': '13',
                'phone': '903-123-4567'
            },
            format='multipart'
        )
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert resp_json
        assert {'Status',} <= set(resp_json.keys())
        assert resp_json.get('Status') is True
        assert Contact.objects.filter(user=user_buyer).count() == 1


    # редактировать контакт пользователя
    def test_user_contact_put(self, api_client, user_buyer, user_buyer_token, contact_factory):
        url = reverse('backend:user-contact')
        contacts = contact_factory(user=user_buyer, _quantity=3)
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + user_buyer_token.key)
        resp = api_client.put(
            url, 
            data={
                'id': contacts[0].id,
                'city': 'Москва',
                'street': 'ул. Строителей',
                'house': '25',
                'structure': '1',
                'building': '1',
                'apartment': '13',
                'phone': '903-123-4567'
            },
            format='multipart'
        )
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert resp_json
        assert {'Status',} <= set(resp_json.keys())
        assert resp_json.get('Status') is True
        assert Contact.objects.filter(id=contacts[0].id).count() == 1
        assert Contact.objects.filter(id=contacts[0].id).first().city == 'Москва'


    # удалить контакт пользователя
    def test_user_contact_delete(self, api_client, user_buyer_token, request, user_buyer, contact_factory):
        url = reverse('backend:user-contact')
        contacts = contact_factory(user=user_buyer, _quantity=3)
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + user_buyer_token.key)
        resp = api_client.delete(
            url, 
            data={
                'items': ','.join([str(contact.id) for contact in contacts]),
            }
        )
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert resp_json
        assert {'Status',} <= set(resp_json.keys())
        assert resp_json.get('Status') is True
        assert Contact.objects.filter(user=user_buyer).count() == 0


    # редактировать пользователя
    def test_user_details_post(self, api_client, user_buyer_token, request, user_buyer):
        url = reverse('backend:user-details')
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + user_buyer_token.key)
        resp = api_client.post(
            url, 
            data={
                'first_name': 'Иван Иванович',
                'last_name': 'Иванов',
                'email': 'sds-diplom-24@mail.ru',
                'password': 'очень_сложный_пароль_12345',
                'company': 'Компания Иванова',
                'position': 'Должность Ианова'
            }
        )
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert resp_json
        assert {'Status',} <= set(resp_json.keys())
        assert resp_json.get('Status') is True
        assert User.objects.get(id=user_buyer.id).first_name == 'Иван Иванович'


    # получить сведения о пользователе
    def test_user_details_get(self, api_client, user_buyer_token, request, user_buyer):
        url = reverse('backend:user-details')
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + user_buyer_token.key)
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert resp_json
        assert {'id', 'first_name', 'last_name', 'email', 'company', 'position'} <= set(resp_json.keys())
        assert resp_json.get('first_name') == user_buyer.first_name



@pytest.mark.django_db
class TestUserVariousToken:

    # подтверждение электронной почты пользователя
    @pytest.mark.parametrize('valid_token', (True, False))
    def test_registration_confirm(self, api_client, valid_token):
        url = reverse('backend:user-register-confirm')
        test_user = User.objects.create_user(email='sds-diplom-24@mail.ru', is_active=False, **NEW_USER_PROFILE_INFO)
        # получить токен для подтверждения электронной почты
        if valid_token:
            # из БД для проверки корректного токена
            user_token = ConfirmEmailToken.objects.get(user__email=test_user.email)
            assert user_token
            key = user_token.key
        else:
            # сгенерировать для проверки некорретного токена
            key = 'wrongtoken'
        # отправить запрос на подтверждение электронной почты пользователя
        resp = api_client.post(
            url,
            {
                'email': test_user.email,
                'token': key
            }
        )
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        # проверить статус ответа исходя из корректности токена
        assert resp_json.get('Status') == valid_token
        # проверить статус пользователя в БД
        created_user = User.objects.get(email=test_user.email)
        assert created_user.is_active == valid_token



@pytest.mark.parametrize('valid_password', (True, False))
@pytest.mark.django_db
class TestUserVariousPass:
    
    # авторизация пользователя
    def test_login(self, api_client, user_buyer, user_buyer_token, valid_password):
        url=reverse('backend:user-login')
        resp = api_client.post(
            url, 
            {
                'email':user_buyer.email, 
                'password': NEW_USER_PROFILE_INFO['password'] if valid_password else 'wrongpassword',
            }
        )
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert resp_json.get('Status') == valid_password
        if valid_password:
            assert resp_json.get('Token') == user_buyer_token.key
        else:
            assert resp_json.get('Errors')
