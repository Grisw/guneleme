import requests
import re
import os


def onQQMessage(bot, contact, member, content):
    if content.startswith('https://url.cn/'):
        content = resume_url_cn(content)

    if not content.startswith('https://h5.ele.me/hongbao/'):
        return

    lucky_number = re.search('lucky_number=(\d+)', content)
    if lucky_number:
        lucky_number = lucky_number.group(1)
    else:
        return

    sn = re.search('sn=(\w{16})', content)
    if sn:
        sn = sn.group(1)
    else:
        return

    requests.post('http://guneleme:8000/coupon/', json={
        'lucky_number': lucky_number,
        'sn': sn,
        'key': os.getenv('COUPON_KEY', 'defaultkey')
    })


def resume_url_cn(url):
    r = requests.get(url, allow_redirects=False)
    return r.headers['Location']
