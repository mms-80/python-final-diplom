from drf_spectacular.utils import inline_serializer, extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework import serializers
from backend.serializers import OrderSerializer
from drf_spectacular.extensions import OpenApiViewExtension


class StatusSerializer(serializers.Serializer):
    Status = serializers.BooleanField()
    Errors = serializers.CharField()


class StatusAuthErrSerializer(serializers.Serializer):
    Status = serializers.BooleanField()
    Error = serializers.CharField(default='Log in required')


class NewTaskSerializer(serializers.Serializer):
    Status = serializers.BooleanField()
    Task_id = serializers.CharField()

class ItemSerializer(serializers.Serializer):
    product_info = serializers.IntegerField()
    quantity = serializers.IntegerField()


class ItemsSerializer(serializers.Serializer):
    items = ItemSerializer(many=True)


class ItemUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    quantity = serializers.IntegerField()


class ItemsUpdateSerializer(serializers.Serializer):
    items = ItemUpdateSerializer(many=True)


class ConfirmEmailSerializer(serializers.Serializer):
    email = serializers.CharField()
    token = serializers.CharField()


class OrderViewSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    contact = serializers.IntegerField()


class FixRegisterAccount(OpenApiViewExtension):
    target_class = 'backend.views.RegisterAccount'

    def view_replacement(self):

        @extend_schema(
            tags=['Users'],
            summary='Register new account',
            request=inline_serializer(
                name='RegisterAccountRequest',
                fields={
                    'first_name': serializers.CharField(),
                    'last_name': serializers.CharField(),
                    'email': serializers.CharField(),
                    'password': serializers.CharField(),
                    'company': serializers.CharField(),
                    'position': serializers.CharField(),
                },
            ),
            responses={
                (200, 'application/json'): StatusSerializer
            },
        )
        class FixedRegisterAccount(self.target_class):
            pass

        return FixedRegisterAccount


class FixLoginAccount(OpenApiViewExtension):
    target_class = 'backend.views.LoginAccount'

    def view_replacement(self):

        @extend_schema(
            tags=['Users'],
            summary='Login to account',
            request=inline_serializer(
                name='LoginAccountRequest',
                fields={
                    'email': serializers.CharField(),
                    'password': serializers.CharField(),
                },
            ),
            responses={
                (200, 'application/json'): inline_serializer(
                        name='LoginAccountResponseOk',
                        fields={
                            'Status': serializers.BooleanField(),
                            'Token': serializers.CharField(),
                        },
                    ),
            },
        )
        class FixedLoginAccount(self.target_class):
            pass

        return FixedLoginAccount


class FixBasketView(OpenApiViewExtension):
    target_class = 'backend.views.BasketView'

    def view_replacement(self):
        
        @extend_schema(
                tags=['Shop'],
                summary='User''s basket',
                responses={
                    (200, 'application/json'): OrderSerializer,
                    (403, 'application/json'): StatusAuthErrSerializer,
                },
            )
        class FixedBasketView(self.target_class):
            @extend_schema(
                summary='Retrieve the items in the user''s basket',
                responses={
                    (200, 'application/json'): OrderSerializer,
                    (403, 'application/json'): StatusAuthErrSerializer,
                },
            )
            def get(self, request, *args, **kwargs):
                pass

            @extend_schema(
                summary='Add an item to the user''s basket',
                request=ItemsSerializer,
                responses={
                    (200, 'application/json'): inline_serializer(
                        name='BasketViewPostOk',
                        fields={
                            'Status': serializers.BooleanField(),
                            'Создано объектов': serializers.CharField(),
                        },
                    ),
                    (403, 'application/json'): StatusAuthErrSerializer,
            },
            )
            def post(self, request, *args, **kwargs):
                pass

            @extend_schema(
                summary='Update the quantity of an item in the user''s basket',
                request=ItemsUpdateSerializer,
                responses={
                    (200, 'application/json'): inline_serializer(
                            name='BasketViewPutOk',
                            fields={
                                'Status': serializers.BooleanField(),
                                'Создано объектов': serializers.CharField(),
                            },
                    ),
                    (403, 'application/json'): StatusAuthErrSerializer,
            },
            )
            def put(self, request, *args, **kwargs):
                pass

            @extend_schema(
                summary='Remove an item from the user''s basket',
                request=ItemsSerializer,
                responses={
                (200, 'application/json'): inline_serializer(
                        name='BasketViewDeleteOk',
                        fields={
                            'Status': serializers.BooleanField(),
                            'Удалено объектов': serializers.CharField(),
                        },
                    ),
            },
            )
            def delete(self, request, *args, **kwargs):
                pass
        
        return FixedBasketView


class FixPartnerExport(OpenApiViewExtension):
    target_class = 'backend.views.PartnerExport'

    def view_replacement(self):

        @extend_schema(
            tags=['Partner'],
            summary='Export partner price in YAML format',
            responses={
                200: inline_serializer(
                        name='PartnerExportResponseOk',
                        fields={
                            'Status': serializers.BooleanField(),
                            'Task_id': serializers.CharField(),
                            'url': serializers.CharField(),
                        },
                    ),
            },
        )
        class FixedPartnerExport(self.target_class):
            pass

        return FixedPartnerExport


class FixPartnerOrders(OpenApiViewExtension):
    target_class = 'backend.views.PartnerOrders'

    def view_replacement(self):

        @extend_schema(
            tags=['Partner'],
        )
        class FixedPartnerOrders(self.target_class):
            @extend_schema(
                summary='Retrieve the orders associated with the authenticated partner',
                responses={
                    (200, 'application/json'): OrderSerializer,
                },
            )
            def get(self, request, *args, **kwargs):
                pass
            
            @extend_schema(
                summary='Update the state of an order',
                responses={
                    (200, 'application/json'): StatusSerializer
                },
            )
            def put(self, request, *args, **kwargs):
                pass

        return FixedPartnerOrders


class FixResultsView(OpenApiViewExtension):
    target_class = 'backend.views.ResultsView'

    def view_replacement(self):

        class FixedResultsView(self.target_class):
            @extend_schema(
                tags=['Common'],
                summary='Get the result of a task executed asynchronously in Celery',
                request=inline_serializer(
                    name='ResultsViewRequest',
                    fields={
                        'email': serializers.CharField(),
                        'password': serializers.CharField(),
                    },
                ),
                responses={
                    (200, 'application/json'): inline_serializer(
                            name='ResultsViewResponseOk',
                            fields={
                                'Status': serializers.BooleanField(),
                                'Token': serializers.CharField(),
                            },
                        ),
                },
            )
            def get(self, request, *args, **kwargs):
                pass

        return FixedResultsView
