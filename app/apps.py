from django.apps import AppConfig
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from django.db.models import F
import random
import logging
import datetime

logger = logging.getLogger('default')


class AppConfig(AppConfig):
    name = 'app'

    def test_coupons(self):
        from app.models import Coupon, Account
        lambs = Account.objects.filter(is_lamb=True)
        if not lambs or len(lambs) == 0:
            return
        luckys = Account.objects.filter(is_lamb=False).order_by('-last_lucky_time')
        if not luckys or len(luckys) == 0:
            return
        lucky = luckys[0]
        coupons = Coupon.objects.filter(lucky_number__gt=F('current_count'))
        for coupon in coupons:
            if coupon.lucky_number - coupon.current_count == 1:
                continue
            if not coupon.lamb_account:
                coupon.lamb_account = random.choice(lambs)
            jo = self.get_coupon(coupon.lamb_account, coupon)
            coupon.current_count = len(jo['promotion_records'])
            if coupon.lucky_number - coupon.current_count == 1:
                logger.info('Next max! sn: {sn}, lucky guy: {lucky}'.format(sn=coupon.sn, lucky=lucky.openid))
                jo = self.get_coupon(lucky, coupon)
                if jo['is_lucky']:
                    lucky.last_lucky_time = datetime.datetime.now()
                    coupon.lucky_account = lucky
                    coupon.amount = jo['promotion_records'][-1]['amount']
                    lucky.save()
                    logger.info('Success! sn: {sn}, lucky guy: {lucky}, amount: {amount}'
                                .format(sn=coupon.sn, lucky=lucky.openid, amount=coupon.amount))
                else:
                    logger.info('Failed! sn: {sn}'.format(sn=coupon.sn, lucky=lucky.openid, amount=coupon.amount))
                coupon.current_count = len(jo['promotion_records'])
            else:
                logger.info('sn: {sn}, remains: {remain}.'
                            .format(sn=coupon.sn, remain=coupon.lucky_number - coupon.current_count))
            coupon.save()

    def get_coupon(self, account, coupon):
        logger.info('{{"method":"phone","group_sn":"{sn}","sign":"{sign}"}}'.format(sn=coupon.sn, sign=account.sign))
        r = requests.post(
            url='https://h5.ele.me/restapi/marketing/promotion/weixin/{openid}'.format(openid=account.openid),
            data='{{"method":"phone","group_sn":"{sn}","sign":"{sign}"}}'.format(sn=coupon.sn,
                                                                                 sign=account.sign),
            headers={
                'Cookie': account.cookies,
                'Content-Type': 'text/plain',
                'User-Agent': 'mozilla/5.0 (Linux; U; Android 5.1; zh-cn; OPPO R9tm Build/LMY47I) AppleWebKit/537.36 (KHTML, like Gecko)Version/4.0 Chrome/37.0.0.0 MQQBrowser/7.5 Mobile Safari/537.36'
            })
        return r.json()

    def ready(self):
        scheduler = BackgroundScheduler()
        scheduler.add_job(self.test_coupons, 'interval', seconds=5)
        scheduler.start()
