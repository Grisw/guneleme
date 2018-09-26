from django.contrib import admin
from app.models import Account, Coupon
import datetime
from django.db.models import F


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('qq', 'is_lamb', 'last_lucky_time', 'temp_lamb_until')
    readonly_fields = ('last_lucky_time', 'temp_lamb_until')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('sn', 'lucky_number', 'current_count', 'lucky_account', 'amount', 'create_time', 'pick_time')
    readonly_fields = ('amount', 'create_time', 'pick_time')
    actions = ('delete_old', )

    class RemainsFilter(admin.SimpleListFilter):
        title = 'Remains Count'
        parameter_name = 'remains'

        def lookups(self, request, model_admin):
            return (
                ('-1', 'Less than 0'),
                ('0', 'Equals to 0'),
                ('1', 'Greater than 0'),
            )

        def queryset(self, request, queryset):
            if self.value() == '-1':
                return queryset.filter(lucky_number__lt=F('current_count'))
            if self.value() == '0':
                return queryset.filter(lucky_number=F('current_count'))
            if self.value() == '1':
                return queryset.filter(lucky_number__gt=F('current_count'))
    list_filter = (RemainsFilter, 'lucky_account', 'lamb_account')

    def delete_old(self, request, queryset):
        olds = Coupon.objects.filter(time__lt=datetime.date.today() - datetime.timedelta(days=1))
        count, rows = olds.delete()
        self.message_user(request, '%s successfully deleted.' % count)
    delete_old.short_description = 'Delete coupons created 1 day ago'
