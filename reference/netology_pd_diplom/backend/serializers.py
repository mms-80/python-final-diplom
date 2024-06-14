# Верстальщик
from rest_framework import serializers

from backend.models import User, Category, Shop, ProductInfo, Product, ProductParameter, OrderItem, Order, Contact


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'user', 'phone')
        read_only_fields = ('id',)
        extra_kwargs = {
            'user': {'write_only': True}
        }


class UserSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'company', 'position', 'contacts')
        read_only_fields = ('id',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name',)
        read_only_fields = ('id',)


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name', 'state',)
        read_only_fields = ('id',)


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ('name', 'category',)


class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = serializers.StringRelatedField()

    class Meta:
        model = ProductParameter
        fields = ('parameter', 'value',)


class ProductInfoSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_parameters = ProductParameterSerializer(read_only=True, many=True)

    class Meta:
        model = ProductInfo
        fields = ('id', 'model', 'product', 'shop', 'quantity', 'price', 'price_rrc', 'product_parameters',)
        read_only_fields = ('id',)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'product_info', 'quantity', 'order',)
        read_only_fields = ('id',)
        extra_kwargs = {
            'order': {'write_only': True}
        }


class OrderItemCreateSerializer(OrderItemSerializer):
    product_info = ProductInfoSerializer(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    ordered_items = OrderItemCreateSerializer(read_only=True, many=True)

    total_sum = serializers.IntegerField()
    contact = ContactSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'ordered_items', 'state', 'dt', 'total_sum', 'contact',)
        read_only_fields = ('id',)


# сериализатор для экспорта товаров партнера (магазина) - список параметров товаров
class PartnerProductParameterSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductParameter
        fields = ('parameter.name', 'value',)


# сериализатор для экспорта товаров партнера (магазина) - список товаров
class PartnerProductInfoSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='product.category.name')
    name = serializers.CharField(source='product.name')
    parameters = serializers.SerializerMethodField()

    class Meta:
        model = ProductInfo
        fields = ('id', 'category', 'model', 'name', 'price', 'price_rrc', 'quantity', 'parameters',)
        read_only_fields = ('id',)

    def get_parameters(self, obj):
        return [{param.parameter.name: param.value} for param in obj.product_parameters.all()]


# сериализатор для экспорта товаров партнера (магазина)
class PartnerExportSerializer(serializers.ModelSerializer):
    shop = serializers.CharField(source='name')
    categories = CategorySerializer(read_only=True, many=True)
    goods = PartnerProductInfoSerializer(source='product_infos', read_only=True, many=True)

    class Meta:
        model = Shop
        fields = ('shop', 'categories', 'goods')