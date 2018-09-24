import cv2
import numpy as np
import urllib.request


def __url_to_image(url):
    # download the image, convert it to a NumPy array, and then read
    # it into OpenCV format
    resp = urllib.request.urlopen(url)
    # bytearray将数据转换成（返回）一个新的字节数组
    # asarray 复制数据，将结构化数据转换成ndarray
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    # cv2.imdecode()函数将数据解码成Opencv图像格式
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    # return the image
    return image


def __edge(image):
    blurred = cv2.GaussianBlur(image, (3, 3), 0)
    gray = cv2.cvtColor(blurred, cv2.COLOR_RGB2GRAY)
    return cv2.Canny(gray, 50, 150)


def get_target_pos(url_bg, url_template, bg_width):
    # 加载原始RGB图像
    img_rgb = __url_to_image(url_bg)

    img_edge = __edge(img_rgb)

    # 加载将要搜索的图像模板
    template = __url_to_image(url_template)

    # 记录图像模板的尺寸
    w, h = template.shape[:2]

    template_edge = __edge(template[int(w / 4):int(3 * w / 4), int(h / 4):int(3 * h / 4)])

    # 设定阈值
    threshold = 0.9
    loc = None
    while not loc or (threshold > 0 and len(loc[0]) == 0):
        res = cv2.matchTemplate(img_edge, template_edge, cv2.TM_CCORR_NORMED)
        loc = np.where(res >= threshold)
        threshold -= 0.1

    we = template_edge.shape[0]

    # 使用灰度图像中的坐标对原始RGB图像进行标记
    for pt in zip(*loc[::-1]):
        return int(((pt[0] + we / 2) / (img_rgb.shape[1] - we)) * bg_width)
    return None
