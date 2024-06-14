"""netology_pd_diplom URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import time
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.http import HttpResponse


def trigger_error(request):
    # unhandled error to test Sentry
    division_by_zero = 1 / 0

    # # solution to fix error, which founded by Sentry
    # try:
    #     division_by_zero = 1 / 0
    # except:
    #     division_by_zero = "Hello World"

    # return HttpResponse(division_by_zero)


def large_resource(request):
    time.sleep(4)
    return HttpResponse("Done!")


urlpatterns = [
    path('jet/', include('jet.urls', 'jet')),  # Django JET URLS
    path('admin/', admin.site.urls),
    path('api/v1/', include('backend.urls', namespace='backend')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'), 
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('silk/', include('silk.urls', namespace='silk')),
    # тест использования Sentry для отслеживания ошибок
    path('sentry-debug/', trigger_error),
    # тест использования Sentry для поиска проблем с производительностью
    path('large_resource/', large_resource),
]
