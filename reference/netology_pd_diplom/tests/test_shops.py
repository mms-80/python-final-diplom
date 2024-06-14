import pytest
from django.urls import reverse
from rest_framework import status
from backend.models import User, Shop, Product, Order, OrderItem
from backend.serializers import ProductInfoSerializer


@pytest.mark.django_db
class TestShop:

    # получить список категорий
    def test_categories_get(self, api_client, category_factory):
        url = reverse('backend:categories')
        categories = category_factory(_quantity=3)
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert {'count', 'results'}.issubset(resp_json.keys())
        assert resp_json.get('count') == 3
        assert resp_json.get('results')[0]
        names = set()
        for category in categories:
            names |= {category.name}
        assert resp_json.get('results')[0].get('name') in names


    # получить список магазинов
    def test_shops_get(self, api_client, user_shop):
        url = reverse('backend:shops')
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert {'results',}.issubset(resp_json.keys())
        assert resp_json.get('results')[0].get('name') == Shop.objects.first().name


    # получить список продуктов
    @pytest.mark.django_db
    def test_products_get(self, api_client, shop_products):
        url = reverse('backend:products')
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert len(resp_json) == Product.objects.count()
        assert set(ProductInfoSerializer.Meta.fields) <= set(resp_json[0].keys())


    # получить список продуктов с использованием фильтра
    @pytest.mark.django_db
    def test_products_search(self, api_client, shop_products):
        url = reverse('backend:products')
        resp = api_client.get(f'{url}?shop_id=0&category_id=0')
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert len(resp_json) == 0


    # добавить товары в корзину
    def test_basket_post(self, api_client, user_buyer, user_buyer_token, shop_products):
        url = reverse('backend:basket')
        basket = []  
        for product in shop_products[:2]:
            basket_item = f'{{"product_info":{product.product_infos.first().id}, "quantity": 3}}'
            basket.append(basket_item)
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + user_buyer_token.key)
        resp = api_client.post(
            url, 
            {
                'items': f'[{','.join(basket)}]'
            }
        )
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert resp_json.get('Status') is True
        assert Order.objects.filter(state='basket',user=user_buyer).count() == 1
        assert OrderItem.objects.filter(order=Order.objects.filter(state='basket',user=user_buyer).first()).count() == 2


    # изменить число товаров в корзине
    def test_basket_update(self, api_client, user_buyer_token, shop_products, basket):
        url = reverse('backend:basket')
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + user_buyer_token.key)
        basket_update = []
        order_items_ids = []
        for ordered_item in basket.ordered_items.all()[:2]:
            basket_item = f'{{"id":{ordered_item.id}, "quantity": 8}}'
            basket_update.append(basket_item)
            order_items_ids.append(ordered_item.id)
        resp = api_client.put(
            url, 
            {
                'items': f'[{','.join(basket_update)}]'
            }
        )
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert resp_json.get('Status') is True
        for order_item_id in order_items_ids:
            assert OrderItem.objects.filter(id=order_item_id).first().quantity == 8


    # удалить товары из корзины
    def test_basket_del_items(self, api_client, user_buyer_token, shop_products, basket):
        url = reverse('backend:basket')
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + user_buyer_token.key)
        old_items_num = basket.ordered_items.count()
        resp = api_client.delete(
            url, 
            {
                'items': ','.join([str(ordered_item.id) for ordered_item in basket.ordered_items.all()[:2]])
            }
        )
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert resp_json.get('Status') is True
        assert OrderItem.objects.filter(order=basket).count() < old_items_num


    # получить содержимое корзины
    def test_basket_get(self, api_client, user_buyer_token, shop_products, basket):
        url = reverse('backend:basket')
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + user_buyer_token.key)
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert {'id', 'ordered_items', 'state', 'dt', 'total_sum', 'contact'}.issubset(resp_json[0].keys())
        assert resp_json[0].get('id') == basket.id
        assert len(resp_json[0].get('ordered_items')) == basket.ordered_items.count()


    # получить заказы пользователя
    def test_order_get(self, api_client, user_buyer_token, shop_products, shop_orders):
        url = reverse('backend:order')
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + user_buyer_token.key)
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert len(resp_json) == len([order for order in shop_orders if order.state != 'basket'])
        assert {'id', 'ordered_items', 'state', 'dt', 'total_sum', 'contact'}.issubset(resp_json[0].keys())


    # разместить заказ
    def test_order_post(self, api_client, user_buyer_token, shop_products, basket):
        url = reverse('backend:order')
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + user_buyer_token.key)
        data = {'id': str(basket.id), 'contact': str(basket.contact.pk)}
        resp = api_client.post(url, data)
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert {'Status',}.issubset(resp_json.keys())
        assert resp_json.get('Status') is True
        Order.objects.get(id=basket.id).state == 'new'