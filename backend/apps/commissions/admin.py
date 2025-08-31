from django.contrib import admin
from .models import MonthlyCommissionReport

@admin.register(MonthlyCommissionReport)
class MonthlyCommissionReportAdmin(admin.ModelAdmin):
    list_display = ('seller', 'period_display', 'total_sales_amount', 'total_commission', 'status')
    list_filter = ('seller', 'year', 'month', 'status')
    search_fields = ('seller__username', 'seller__first_name', 'seller__last_name')
    readonly_fields = ('total_sales_amount', 'total_commission', 'average_commission_rate')
    ordering = ('-year', '-month')

    def period_display(self, obj):
        return obj.period_display
    period_display.short_description = 'Período'
    period_display.admin_order_field = 'month'  
    