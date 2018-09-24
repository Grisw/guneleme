from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
from app.captcha import get_target_pos
from threading import Timer
import time
from urllib import parse
import json
from guneleme.settings import ELEME_TEST_COUPON

logger = logging.getLogger('default')
LOGIN_READY_DICT = {}


def __wait_for_visible(wait, xpath):
    return wait.until(expected_conditions.visibility_of_element_located((By.XPATH, xpath)))


def start_login(qq, password, phone):
    # Start browser
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('user-agent="Mozilla/5.0(iPhone;CPUiPhoneOS10_2_1likeMacOSX)AppleWebKit/602.4.6(KHTML,likeGecko)Mobile/14D27QQ/6.7.1.416V1_IPH_SQ_6.7.1_1_APP_APixel/750Core/UIWebViewNetType/4GQBWebViewType/1"')
    retry_count = 0
    while True:
        try:
            browser = webdriver.Chrome(chrome_options=options)
            break
        except ConnectionResetError as e:
            retry_count += 1
            if retry_count >= 10:
                raise e
    browser.set_page_load_timeout(60)
    wait = WebDriverWait(browser, 10)
    logger.info('"{qq}" is logging in.'.format(qq=qq))
    try:
        browser.get(ELEME_TEST_COUPON)
    except TimeoutException:
        pass
    qq_input = __wait_for_visible(wait, '//*[@id="u"]')
    passwd_input = browser.find_element_by_xpath('//*[@id="p"]')
    login_btn = browser.find_element_by_xpath('//*[@id="go"]')

    qq_input.send_keys(qq)
    passwd_input.send_keys(password)
    login_btn.click()

    try:
        iframe = __wait_for_visible(wait, '//*[@id="tcaptcha_iframe"]')
        logger.info('"{qq}" requires captcha.'.format(qq=qq))
        browser.switch_to.frame(iframe)
        img_bg = __wait_for_visible(wait, '//*[@id="bkBlock"]')
        img_template = __wait_for_visible(wait, '//*[@id="slideBlock"]')
        drag_btn = __wait_for_visible(wait, '//*[@id="tcaptcha_drag_button"]')
        pos = get_target_pos(img_bg.get_attribute('src'), img_template.get_attribute('src'), img_bg.size['width'] - drag_btn.size['width'])
        if pos is None:
            raise Exception('Untrackable images.')
        browser.execute_script('arguments[0].style = "left: {pos}px;";'.format(pos=pos), img_template)
        drag_btn.click()
        browser.switch_to.default_content()
        logger.info('"{qq}" captcha pass.'.format(qq=qq))
    except TimeoutException:
        pass
    retry_count = 0
    while True:
        try:
            phone_input = __wait_for_visible(wait, '/html/body/div[1]/div[1]/div[2]/form/div[1]/input')
            break
        except TimeoutException:
            retry_count += 1
            if retry_count >= 5:
                logger.info('"{qq}" login failed.'.format(qq=qq))
                return False, None
    logger.info('"{qq}" login success.'.format(qq=qq))
    code_btn = __wait_for_visible(wait, '/html/body/div[1]/div[1]/div[2]/form/div[1]/button')
    phone_input.send_keys(phone)
    code_btn.click()

    timer = Timer(300, release, [qq, browser])
    if qq in LOGIN_READY_DICT:
        release(qq, LOGIN_READY_DICT[qq][0])
    LOGIN_READY_DICT[qq] = [browser, timer]
    try:
        captcha_img = __wait_for_visible(wait, '/html/body/div[1]/div[1]/div[2]/div[3]/div/div[1]/img')
        timer.start()
        return True, captcha_img.get_attribute('src')
    except TimeoutException:
        timer.start()
        return True, None


def input_captcha_img(qq, captcha):
    if qq not in LOGIN_READY_DICT:
        return False, None
    browser, timer = LOGIN_READY_DICT[qq]
    timer.cancel()
    captcha_input = browser.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[3]/div/div[1]/div/input')
    confirm_btn = browser.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[3]/div/div[2]/button[2]')
    captcha_input.send_keys(captcha)
    confirm_btn.click()
    time.sleep(1)
    timer = LOGIN_READY_DICT[qq][1] = Timer(300, release, [qq, browser])
    timer.start()
    try:
        captcha_img = browser.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[3]/div/div[1]/img')
        return False, captcha_img.get_attribute('src')
    except NoSuchElementException:
        return True, None


def submit_code(qq, code):
    if qq not in LOGIN_READY_DICT:
        return None
    browser, timer = LOGIN_READY_DICT[qq]
    timer.cancel()
    code_input = browser.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/form/div[2]/input')
    code_input.send_keys(code)
    submit_btn = browser.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/form/button')
    submit_btn.click()

    wait = WebDriverWait(browser, 30)
    try:
        __wait_for_visible(wait, '/html/body/div[1]/div[1]/div[2]/div[4]/p[1]/span[1]')
        cookies = browser.get_cookies()
        cookies_formatted = []
        sign = None
        openid = None
        for cookie in cookies:
            if 'ele.me' in cookie['domain']:
                cookies_formatted.append('{name}={value}'.format(name=cookie['name'], value=cookie['value']))
                if 'snsInfo' in cookie['name']:
                    json_str = parse.unquote(cookie['value'])
                    jo = json.loads(json_str)
                    sign = jo['eleme_key']
                    openid = jo['openid']
        release(qq, browser)
        return {
            'sign': sign,
            'openid': openid,
            'cookies': '; '.join(cookies_formatted)
        }
    except TimeoutException:
        timer = LOGIN_READY_DICT[qq][1] = Timer(300, release, [qq, browser])
        timer.start()
        return None


def release(qq, browser):
    if browser:
        browser.quit()
    if qq in LOGIN_READY_DICT:
        LOGIN_READY_DICT[qq][1].cancel()
        LOGIN_READY_DICT.pop(qq)
    logger.info('"{qq}" browser exit.'.format(qq=qq))

