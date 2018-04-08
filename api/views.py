#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import importlib
from django.views import View
from django.http import JsonResponse
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from utils import auth
from api import config
from repository import models
from api.service import asset


class AssetView(View):
    @method_decorator(csrf_exempt)  # 注意，在CBV中，不想再使用csrf验证时，要将装饰函数放在dispath上，不能单独放在某个（POST）函数上，那样不起作用
    def dispatch(self, request, *args, **kwargs):
        return super(AssetView, self).dispatch(request, *args, **kwargs)

    @method_decorator(auth.api_auth)
    def get(self, request, *args, **kwargs):
        """
        获取今日未更新的资产 - 适用SSH或Salt客户端
        :param request:
        :param args:
        :param kwargs:
        :return:
        1.今日未更新
        2.资产状态是在线
        models.tb.objects.filter(f1=1, f2=2)
        models.tb.objects.filter(**{f1:xx,f})
        Q1对象{内部OR：id=1,name='alex'}
        Q2对象{内部OR：id=1,name='alex'}
        Q(Q1,and,Q2)
        """

        # test = {'user': '用户名', 'pwd': '密码'}
        # result = json.dumps(test,ensure_ascii=True)
        # result = json.dumps(test,ensure_ascii=False)
        # return HttpResponse(result)

        # test = {'user': '用户名', 'pwd': '密码'}
        # result = json.dumps(test,ensure_ascii=True)
        # result = json.dumps(test,ensure_ascii=False)
        # return HttpResponse(result,content_type='application/json')

        # test = {'user': '用户名', 'pwd': '密码'}
        # return JsonResponse(test, json_dumps_params={"ensure_ascii": False})

        response = asset.get_untreated_servers()
        return JsonResponse(response.__dict__)  # JsonResponse在内部实际上就是先进行json.dump将字典转化成字符串，然后通过再返回给用户
        # return JsonResponse({'k1': 'v1'})
        # return JsonResponse([1, 2, 3], safe=False)  # 如果是列表，必须要加上safe=False

    @method_decorator(auth.api_auth)
    def post(self, request, *args, **kwargs):
        """
        更新或者添加资产信息
        :param request:
        :param args:
        :param kwargs:
        :return: 1000 成功;1001 接口授权失败;1002 数据库中资产不存在
        """
        # 如果是request.POST，它只能拿请求是URL=FORMDATA的数据，如果传过来是JSON数据，request.POST是拿不到的，只能从request.body提取出来
        server_info = json.loads(request.body.decode('utf-8'))
        server_info = json.loads(server_info)  # {'hostname':..., 'version': ....., 'disk': .....}
        hostname = server_info['hostname']

        ret = {'code': 1000, 'message': '[%s]更新完成' % hostname}
        # 根据主机名获取服务器信息
        server_obj = models.Server.objects.filter(hostname=hostname).select_related('asset').first()
        if not server_obj:
            ret['code'] = 1002
            ret['message'] = '[%s]资产不存在' % hostname
            return JsonResponse(ret)

        for k, v in config.PLUGINS_DICT.items():
            module_path, cls_name = v.rsplit('.', 1)
            cls = getattr(importlib.import_module(module_path), cls_name)
            response = cls.process(server_obj, server_info, None)
            if not response.status:
                ret['code'] = 1003
                ret['message'] = "[%s]资产更新异常" % hostname
            if hasattr(cls, 'update_last_time'):
                cls.update_last_time(server_obj, None)

        return JsonResponse(ret)
