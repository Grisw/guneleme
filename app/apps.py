from django.apps import AppConfig
import requests
from django.db.models import F, Q
import random
import logging
import datetime
from threading import Timer

logger = logging.getLogger('default')


class AppConfig(AppConfig):
    name = 'app'
    Account = None
    Coupon = None
    interval = 4

    def test_coupons(self):
        # Get Available Lambs and Luckys.
        lambs = self.get_lambs()
        if not lambs:
            Timer(self.interval, self.test_coupons).start()
            return
        luckys = self.get_luckys()
        if not luckys:
            Timer(self.interval, self.test_coupons).start()
            return
        # Circular iteration, start from 0
        current_lucky = 0

        coupons = self.get_coupons()
        for coupon in coupons:
            # Choose lamb account.
            if not coupon.lamb_account:
                coupon.lamb_account = random.choice(lambs)

            jo = self.pick_coupon(coupon.lamb_account, coupon)
            if 'promotion_records' not in jo:
                # IP was ban, retry next time. No need to update coupon.lamb_account.
                continue

            coupon.current_count = len(jo['promotion_records'])
            if coupon.lucky_number - coupon.current_count == 1:
                # When next is biggest, choose lucky account.
                if not coupon.lucky_account:
                    lucky = luckys[current_lucky]
                    current_lucky = (current_lucky + 1) % len(luckys)
                else:
                    lucky = coupon.lucky_account

                logger.info('Next max! sn: {sn}, lucky guy: {lucky}'.format(sn=coupon.sn, lucky=lucky.qq))
                jo = self.pick_coupon(lucky, coupon)

                # If this account is full, turn to next account in luckys, until all luckys are iterated.
                _current_lucky = current_lucky - 1
                while 'is_lucky' not in jo and _current_lucky != current_lucky:
                    if _current_lucky == -1:
                        import json
                        logger.debug(json.dumps(jo))
                        break
                    if jo:
                        # This account is full, set it as temp lamb until next day.
                        lucky.temp_lamb_until = datetime.date.today() + datetime.timedelta(days=1)
                        lucky.save()
                        logger.info('Full! lucky guy: {lucky}, change it to lamb until: {temp_lamb_until}'
                                    .format(lucky=lucky.qq, temp_lamb_until=lucky.temp_lamb_until))
                    # Turn to next account.
                    lucky = luckys[current_lucky]
                    current_lucky = (current_lucky + 1) % len(luckys)
                    jo = self.pick_coupon(lucky, coupon)
                if 'is_lucky' not in jo:
                    # All account in luckys are full, save coupon status immediately.
                    coupon.current_count = len(jo['promotion_records'])
                    coupon.save()
                    continue

                if jo['is_lucky']:
                    # If success, update lucky time.
                    lucky.last_lucky_time = datetime.datetime.now()
                    lucky.save()
                    coupon.pick_time = lucky.last_lucky_time
                    coupon.lucky_account = lucky
                    coupon.amount = jo['promotion_records'][-1]['amount']
                    logger.info('Success! sn: {sn}, lucky guy: {lucky}, amount: {amount}'
                                .format(sn=coupon.sn, lucky=lucky.qq, amount=coupon.amount))
                else:
                    logger.info('Failed! sn: {sn}'.format(sn=coupon.sn))
                coupon.current_count = len(jo['promotion_records'])
            else:
                logger.debug('sn: {sn}, remains: {remain}.'.format(sn=coupon.sn, remain=coupon.lucky_number - coupon.current_count))
            coupon.save()
        Timer(self.interval, self.test_coupons).start()

    def get_lambs(self):
        lambs = self.Account.objects.filter(Q(is_lamb=True) | Q(temp_lamb_until__gt=datetime.datetime.now()))
        if not lambs or len(lambs) == 0:
            return None
        return lambs

    def get_luckys(self):
        luckys = self.Account.objects.filter(is_lamb=False, temp_lamb_until__lte=datetime.datetime.now())
        if not luckys or len(luckys) == 0:
            return None
        return luckys.order_by('last_lucky_time')

    def get_coupons(self):
        coupons = self.Coupon.objects.filter(lucky_number__gt=F('current_count'), create_time__gte=datetime.date.today() - datetime.timedelta(days=1))
        if not coupons or len(coupons) == 0:
            return []
        return coupons

    def pick_coupon(self, account, coupon):
        try:
            r = requests.post(
                url='https://h5.ele.me/restapi/marketing/promotion/weixin/{openid}'.format(openid=account.openid),
                data='{{"method":"phone","group_sn":"{sn}","sign":"{sign}"}}'.format(sn=coupon.sn, sign=account.sign),
                headers={
                    'Cookie': account.cookies,
                    'Content-Type': 'text/plain',
                    'User-Agent': 'mozilla/5.0 (Linux; U; Android 5.1; zh-cn; OPPO R9tm Build/LMY47I) AppleWebKit/537.36 (KHTML, like Gecko)Version/4.0 Chrome/37.0.0.0 MQQBrowser/7.5 Mobile Safari/537.36'
                })
            return r.json()
        except IOError as e:
            logger.error(e.args)
            return {}

    def ready(self):
        from app.models import Coupon, Account
        self.Coupon = Coupon
        self.Account = Account
        Timer(self.interval, self.test_coupons).start()
