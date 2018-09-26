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

    class CreateTimeFilter(admin.SimpleListFilter):
        title = 'Create Time'
        parameter_name = 'create_time'

        def lookups(self, request, model_admin):
            return (
                ('-2', 'Before yesterday'),
                ('-1', 'Yesterday'),
                ('0', 'Today'),
            )

        def queryset(self, request, queryset):
            if self.value() == '-2':
                return queryset.filter(create_time__lt=datetime.date.today() - datetime.timedelta(days=1))
            if self.value() == '-1':
                return queryset.filter(create_time__gte=datetime.date.today() - datetime.timedelta(days=1), create_time__lt=datetime.date.today())
            if self.value() == '0':
                return queryset.filter(create_time__gte=datetime.date.today())

    list_filter = (RemainsFilter, CreateTimeFilter, 'lucky_account', 'lamb_account')
