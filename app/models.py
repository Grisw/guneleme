from django.db import models
import datetime


class Account(models.Model):
    qq = models.CharField(primary_key=True, max_length=20)
    password = models.CharField(max_length=50)
    phone = models.CharField(max_length=11)
    is_lamb = models.BooleanField()
    openid = models.CharField(max_length=32, null=True)
    sign = models.CharField(max_length=32, null=True)
    cookies = models.TextField(null=True)
    last_lucky_time = models.DateTimeField(default=datetime.datetime.now())


class Coupon(models.Model):
    sn = models.CharField(primary_key=True, max_length=16)
    lucky_number = models.IntegerField()
    current_count = models.IntegerField(default=0)
    lamb_account = models.ForeignKey(Account, models.SET_NULL, to_field='qq', null=True, related_name='lamb')
    lucky_account = models.ForeignKey(Account, models.SET_NULL, to_field='qq', null=True, related_name='lucky')
    amount = models.FloatField(default=0)
