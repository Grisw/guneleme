import requests
import re
import os
import django
import sys
from django.db import IntegrityError
import logging
import datetime

logger = logging.getLogger('default')
DCoupon = None


def onInit(bot):
    sys.path.append('/app')
    settings_path = 'guneleme.settings'
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_path)
    django.setup()
    from app.models import Coupon
    global DCoupon
    DCoupon = Coupon


def onQQMessage(bot, contact, member, content):
    if content.startswith('https://url.cn/'):
        content = resume_url_cn(content)

    if not content.startswith('https://h5.ele.me/hongbao/'):
        return

    sn = re.search('sn=(\w{16})', content)
    if sn:
        sn = sn.group(1)
    else:
        return

    lucky_number = re.search('lucky_number=(\d+)', content)
    if lucky_number:
        lucky_number = lucky_number.group(1)
    else:
        return

    if lucky_number == '0':
        lucky_number = resume_lucky_number(sn)

    logger.info(f'GET Coupon: {content}')
    try:
        DCoupon.objects.create(sn=sn, lucky_number=lucky_number, time=datetime.datetime.now())
    except IntegrityError:
        pass


def resume_url_cn(url):
    r = requests.get(url, allow_redirects=False)
    return r.headers['Location']


def resume_lucky_number(sn):
    r = requests.get(f'https://h5.ele.me/restapi/marketing/themes/3113/group_sns/{sn}')
    return r.json()['lucky_number']
