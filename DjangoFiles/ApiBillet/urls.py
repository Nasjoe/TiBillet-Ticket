from django.urls import include, path, re_path

# from BaseBillet import views as base_view
from ApiBillet import views as api_view
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'events', api_view.EventsViewSet, basename='event')
router.register(r'products', api_view.ProductViewSet, basename='product')
router.register(r'prices', api_view.TarifBilletViewSet, basename='price')


urlpatterns = [
    path('', include(router.urls)),
]