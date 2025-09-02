from django.contrib import admin
from .models import DailySales

@admin.register(DailySales)
class DailySalesAdmin(admin.ModelAdmin):
    list_display = ('seller', 'sale_date', 'total_amount', 'commission_rate_applied', 'calculated_commission', 'is_active')
    list_filter = ('seller', 'sale_date', 'is_active')  