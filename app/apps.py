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
    Account = None
    Coupon = None

    def test_coupons(self):
        lambs = self.Account.objects.filter(is_lamb=True)
        if not lambs or len(lambs) == 0:
            return
        luckys = self.Account.objects.filter(is_lamb=False).order_by('last_lucky_time')
        if not luckys or len(luckys) == 0:
            return
        current_lucky = 0
        coupons = self.Coupon.objects.filter(lucky_number__gt=F('current_count'))
        for coupon in coupons:
            if coupon.lucky_number - coupon.current_count == 1:
                continue
            if not coupon.lamb_account:
                coupon.lamb_account = random.choice(lambs)
            if not coupon.lucky_account:
                lucky = luckys[current_lucky]
                current_lucky = (current_lucky + 1) % len(luckys)
            else:
                lucky = coupon.lucky_account

            jo = self.get_coupon(coupon.lamb_account, coupon)
            if 'promotion_records' not in jo:
                continue
            coupon.current_count = len(jo['promotion_records'])
            if coupon.lucky_number - coupon.current_count == 1:
                logger.info('Next max! sn: {sn}, lucky guy: {lucky}'.format(sn=coupon.sn, lucky=lucky.qq))
                jo = self.get_coupon(lucky, coupon)

                _current_lucky = current_lucky - 1
                while 'is_lucky' not in jo and _current_lucky != current_lucky:
                    lucky.last_lucky_time = datetime.date.today() + datetime.timedelta(days=1)
                    lucky.save()
                    logger.info('Full! lucky guy: {lucky}, last_lucky_time push to: {last_lucky_time}'
                                .format(lucky=lucky.qq, last_lucky_time=lucky.last_lucky_time))
                    lucky = luckys[current_lucky]
                    current_lucky = (current_lucky + 1) % len(luckys)
                    jo = self.get_coupon(lucky, coupon)
                if 'is_lucky' not in jo:
                    coupon.current_count = len(jo['promotion_records'])
                    coupon.save()
                    continue

                if jo['is_lucky']:
                    lucky.last_lucky_time = datetime.datetime.now()
                    coupon.lucky_account = lucky
                    coupon.amount = jo['promotion_records'][-1]['amount']
                    lucky.save()
                    logger.info('Success! sn: {sn}, lucky guy: {lucky}, amount: {amount}'
                                .format(sn=coupon.sn, lucky=lucky.qq, amount=coupon.amount))
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
        from app.models import Coupon, Account
        self.Coupon = Coupon
        self.Account = Account
        scheduler = BackgroundScheduler()
        scheduler.add_job(self.test_coupons, 'interval', seconds=5)
        scheduler.start()
