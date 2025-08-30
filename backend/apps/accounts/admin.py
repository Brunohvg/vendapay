from atexit import register
from django.contrib import admin
from .models import Account

@admin.register(Account)
class AccountModelAdmin(admin.ModelAdmin):
    list_display = ('username', 'user_type', 'document', )
    search_fields = ('user_type',)