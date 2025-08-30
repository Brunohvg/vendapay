from django.db import router
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import SaleModelViewSet 


router = DefaultRouter()
router.register(r'sales', SaleModelViewSet, basename='sale')  # gera /sale

urlpatterns = [
    path('', include(router.urls)),  # -> /api/v1/accounts/users/

]   