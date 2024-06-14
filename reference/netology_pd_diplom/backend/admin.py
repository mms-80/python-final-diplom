from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import F, Sum

from backend.models import User, Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, \
    Contact, ConfirmEmailToken


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Панель управления пользователями
    """
    model = User

    fieldsets = (
        (None, {'fields': ('email', 'password', 'type')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'company', 'position')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    pass


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    pass


# список позиций заказа
class OrderItemsInline(admin.TabularInline):
    model = OrderItem
    list_display = ('product_info', 'get_item_price', 'quantity', 'get_item_shop',)
    readonly_fields = list_display
    can_delete = False

    @admin.display(description='Цена')
    def get_item_price(self, obj):
        return obj.product_info.price

    @admin.display(description='Магазин')
    def get_item_shop(self, obj):
        return obj.product_info.shop


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemsInline, ]
    list_display = ('user', 'dt', 'state', 'contact', 'order_sum')
    readonly_fields = ('user', 'dt', 'contact', 'order_sum')

    # итоговая сумма заказа
    @admin.display(description='Сумма заказа (итого)')
    def order_sum(self, obj):
        total_sum = obj.ordered_items.aggregate(total_sum=Sum(F('quantity') * F('product_info__price')))
        return total_sum.get('total_sum')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    pass


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    pass


@admin.register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'created_at',)
