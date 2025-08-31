# apps/commissions/urls.py
from rest_framework.routers import DefaultRouter
from .views import MonthlyCommissionReportViewSet

router = DefaultRouter()
router.register(r'monthly-reports', MonthlyCommissionReportViewSet, basename='monthly-report')

urlpatterns = router.urls
