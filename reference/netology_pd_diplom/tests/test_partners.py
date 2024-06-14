import pytest
from django.urls import reverse
from rest_framework import status
from backend.models import Shop, Order

@pytest.mark.django_db
class TestPartner:

    # обновить прайс партнера - проверка
    def test_partner_update(self, api_client, user_new_shop_token):
        url = reverse('backend:partner-update')
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + user_new_shop_token.key)
        data = {'url': 'https://raw.githubusercontent.com/bku4erov/py-diplom/master/data/shop1.yaml'}
        resp = api_client.post(url, data)
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert resp_json.get('Status') is True
        assert resp_json.get('Task_id')


    # получить статус партнера - проверка
    def test_partner_state_get(self, api_client, user_shop_token):
        url = reverse('backend:partner-state')
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + user_shop_token.key)
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert {'name', 'state',}.issubset(resp_json.keys())


    # обновить статус партнера
    def test_partner_state_post(self, api_client, user_shop_token):
        url = reverse('backend:partner-state')
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + user_shop_token.key)
        resp = api_client.post(url, {'state': 'false'})
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert {'Status', }.issubset(resp_json.keys())
        assert resp_json.get('Status') is True
        assert Shop.objects.first().state is False


    # получить сформированные заказы - проверка
    def test_partner_orders_get(self, api_client, shop_orders, user_shop_token):
        url = reverse('backend:partner-orders')
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + user_shop_token.key)
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert len(resp_json) == (len(shop_orders)-2)
        assert {'id', 'ordered_items'}.issubset(resp_json[0].keys())


    # обновить статус заказа
    def test_partner_orders_put(self, api_client, shop_orders, user_shop_token):
        url = reverse('backend:partner-orders')
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + user_shop_token.key)
        resp = api_client.put(
            url, 
            {        
                'id': shop_orders[0].id, 
                'state': 'sent'
            }
        )
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert resp_json.get('Status') is True
        assert Order.objects.filter(id=shop_orders[0].id).first().state == 'sent'