from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from app.eleme_login import start_login, submit_code, input_captcha_img
import json


@staff_member_required
def account_login(request):
    if request.method != 'POST':
        return JsonResponse({'code': -1, 'msg': 'Route not found.'})

    qq = request.POST.get('qq')
    password = request.POST.get('password')
    phone = request.POST.get('phone')

    if not qq or not password or not phone:
        return JsonResponse({'code': -2, 'msg': 'Params error.'})

    result, captcha = start_login(qq, password, phone)
    if result:
        return JsonResponse({'code': 0, 'msg': 'Success.', 'obj': captcha})
    else:
        return JsonResponse({'code': 1, 'msg': 'Password error?'})


@staff_member_required
def input_captcha(request):
    if request.method != 'POST':
        return JsonResponse({'code': -1, 'msg': 'Route not found.'})

    qq = request.POST.get('qq')
    captcha = request.POST.get('captcha')

    if not qq or not captcha:
        return JsonResponse({'code': -2, 'msg': 'Params error.'})

    result, captcha = input_captcha_img(qq, captcha)
    if result:
        return JsonResponse({'code': 0, 'msg': 'Success.'})
    else:
        if captcha is None:
            return JsonResponse({'code': 1, 'msg': 'Timeout.'})
        else:
            return JsonResponse({'code': 2, 'msg': 'Captcha error?', 'obj': captcha})


@staff_member_required
def code(request):
    if request.method != 'POST':
        return JsonResponse({'code': -1, 'msg': 'Route not found.'})

    qq = request.POST.get('qq')
    code = request.POST.get('code')

    if not qq or not code:
        return JsonResponse({'code': -2, 'msg': 'Params error.'})

    result = submit_code(qq, code)
    if result:
        return JsonResponse({'code': 0, 'msg': 'Success.', 'obj': json.dumps(result)})
    else:
        return JsonResponse({'code': 1, 'msg': 'Code error or timeout?'})
