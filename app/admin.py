from django.contrib import admin
from app.models import Account, Coupon


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('qq', 'phone', 'is_lamb')
    readonly_fields = ('last_lucky_time', )


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('sn', 'lucky_number', 'current_count', 'lucky_account', 'amount')
    readonly_fields = ('amount', )
