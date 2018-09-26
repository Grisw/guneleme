from django.contrib import admin
from app.models import Account, Coupon
import datetime


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('qq', 'is_lamb', 'last_lucky_time', 'temp_lamb_until')
    readonly_fields = ('last_lucky_time', 'temp_lamb_until')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('sn', 'lucky_account', 'amount', 'create_time', 'pick_time', 'remains_count')
    readonly_fields = ('amount', 'create_time', 'pick_time', 'amount')
    actions = ('delete_old', )

    def remains_count(self, obj):
        return obj.lucky_number - obj.current_count

    def delete_old(self, request, queryset):
        olds = Coupon.objects.filter(time__lt=datetime.date.today() - datetime.timedelta(days=1))
        count, rows = olds.delete()
        self.message_user(request, "%s successfully deleted." % count)
    delete_old.short_description = "Delete coupons created 1 day ago"
