from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AccountViewSet

router = DefaultRouter()
router.register(r'users', AccountViewSet)

urlpatterns = [
    path('', include(router.urls)), # O router já gera as URLs para 'users'
]