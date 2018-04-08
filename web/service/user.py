#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
from django.db.models import Q
from repository import models
from utils.pager import PageInfo
from utils.response import BaseResponse
from django.http.request import QueryDict

from .base import BaseServiceList


class User(BaseServiceList):
    def __init__(self):
        # 查询条件的配置
        condition_config = [
            {'name': 'name', 'text': '用户名', 'condition_type': 'input'},
            {'name': 'email', 'text': '邮箱', 'condition_type': 'input'},
        ]
        # 表格的配置
        table_config = [
            {
                'q': 'id',  # 用于数据库查询的字段，即Model.Tb.objects.filter(*[])
                'title': "ID",  # 前段表格中显示的标题
                'display': 1,  # 是否在前段显示，0表示在前端不显示, 1表示在前端隐藏, 2表示在前段显示
                'text': {'content': "{id}", 'kwargs': {'id': '@id'}},
                'attr': {}  # 自定义属性
            },
            {
                'q': 'name',
                'title': "用户名",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@name'}},
                'attr': {'name': 'name', 'id': '@name', 'origin': '@name', 'edit-enable': 'true',
                         'edit-type': 'input', }
            },
            {
                'q': 'email',
                'title': "邮箱",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@email'}},
                'attr': {'name': 'email', 'id': '@email', 'origin': '@email', 'edit-enable': 'true',
                         'edit-type': 'input', }
            },
            {
                'q': 'mobile',
                'title': "手机",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@mobile'}},
                'attr': {'name': 'mobile', 'id': '@mobile', 'origin': '@mobile', 'edit-enable': 'true',
                         'edit-type': 'input', }
            },
            {
                'q': 'phone',
                'title': "电话",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@phone'}},
                'attr': {'name': 'phone', 'id': '@phone', 'origin': '@phone', 'edit-enable': 'true',
                         'edit-type': 'input', }
            },
            {
                'q': 'id',
                'title': "用户所属组",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@@@users_list'}},
                'attr': {'name': 'name', 'id': '@id', 'origin': '@id', 'edit-enable': 'false',
                         'edit-type': 'select',
                         'global-name': 'users_list'}
            },
            # {
            #     'q': None,
            #     'title': "用户所属组",
            #     'display': 1,
            #     'text': {'content': "{n}", 'kwargs': {'n': '@@users_list'}},
            #     'attr': {'name': 'name', 'id': '@users_id', 'origin': '@users_id', 'edit-enable': 'true',
            #              'edit-type': 'select',
            #              'global-name': 'users_list'}
            # },

        ]
        # 额外搜索条件
        # extra_select = {'server_title': 'SELECT hostname FROM repository_server WHERE repository_server.asset_id=repository_asset.id AND repository_asset.device_type_id=1',}
        extra_select = {}
        super(User, self).__init__(condition_config, table_config, extra_select)

    @property
    def usergroup_list(self):
        values1 = models.UserGroup.objects.values('id', 'name')
        values = models.UserGroup.objects.all()
        # for user_obj in values:
        #     num = user_obj.users.count()
        #     print(num, end='\t')
        # print(values)
        result = map(lambda x: {'id': x.id, 'name': x.name}, values)
        # print('idc_list', result, list(result))
        return list(result)

    @property
    def users_list(self):
        val_set = models.UserProfile.objects.values('id', 'name', 'usergroup__name')
        # for user_obj in val_set:
        #     num = user_obj.usergroup_set.count()
        #     print(num, end='\t')
        # result = map(lambda x: {'id': x.id, 'name': x.name, 'usergroup__name': x.usergroup__name}, val_set)
        result = map(lambda x: {'id': x['id'], 'name': x['name'], 'usergroupname': x['usergroup__name']}, val_set)
        print('val_set', val_set, result)
        # try:
        #     # list(result)
        #     print(list(result))
        # except Exception as e:
        #     print(e)
        return list(result)
        pass

    def fetch_users(self, request):
        response = BaseResponse()
        try:
            ret = {}
            conditions = self.assets_condition(request)

            asset_count = models.UserProfile.objects.filter(conditions).count()
            page_info = PageInfo(request.GET.get('pager', None), asset_count)

            asset_list = models.UserProfile.objects.filter(conditions).extra(select=self.extra_select).values(
                *self.values_list)[page_info.start:page_info.end]
            print('asset_list', list(asset_list))
            ret['table_config'] = self.table_config
            ret['condition_config'] = self.condition_config
            ret['data_list'] = list(asset_list)
            ret['page_info'] = {
                "page_str": page_info.pager(),
                "page_start": page_info.start,
            }
            # ret['global_dict'] = {'usergroup_list': self.usergroup_list}
            ret['global_dict'] = {'usergroup_list': self.usergroup_list, 'users_list': self.users_list}
            print('ret', ret['global_dict'])
            response.data = ret
            response.message = '获取成功'
        except Exception as e:
            response.status = False
            response.message = str(e)

        return response

    @staticmethod
    def delete_users(request):
        response = BaseResponse()
        try:
            delete_dict = QueryDict(request.body, encoding='utf-8')
            id_list = delete_dict.getlist('id_list')
            models.UserProfile.objects.filter(id__in=id_list).delete()
            response.message = '删除成功'
            pass
        except Exception as e:
            response.status = False
            response.message = str(e)
        return response

    @staticmethod
    def put_users(request):
        response = BaseResponse()
        try:
            response.error = []
            put_dict = QueryDict(request.body, encoding='utf-8')
            update_list = json.loads(put_dict.get('update_list'))
            error_count = 0
            for row_dict in update_list:
                nid = row_dict.pop('nid')
                num = row_dict.pop('num')
                try:
                    models.UserProfile.objects.filter(id=nid).update(**row_dict)
                except Exception as e:
                    response.error.append({'num': num, 'message': str(e)})
                    response.status = False
                    error_count += 1
            if error_count:
                response.message = '共%s条,失败%s条' % (len(update_list), error_count,)
            else:
                response.message = '更新成功'
        except Exception as e:
            response.status = False
            response.message = str(e)
        return response

    @staticmethod
    def post_users(request):
        response = BaseResponse()
        try:
            name = request.POST.get('name', None)
            email = request.POST.get('email', None)
            phone = request.POST.get('phone', None)
            mobile = request.POST.get('mobile', None)
            # add_dict = QueryDict(request.body, encoding='utf-8')
            # print('add_dict', add_dict)
            # print(hostname, manage_ip, device_type_id, device_status_id, idc_id, business_unit_id)
            t_dict = {'name': name, 'email': email, 'phone': phone, 'mobile': mobile}
            print(t_dict)
            error_count = 0
            idc_obj = models.UserProfile.objects.filter(**t_dict)
            if idc_obj:
                response.message = '添加的IDC信息已经存在'
                response.status = False
                response.error = '错误代码1'
                pass
            else:
                try:
                    models.UserProfile.objects.create(**t_dict)
                except Exception as e:
                    response.error = str(e)
                    response.status = False
                    error_count += 1
                if error_count:
                    response.message = '添加IDC信息失败'
                else:
                    response.message = '添加IDC信息成功'
        except Exception as e:
            response.status = False
            response.message = str(e)
        return response
        pass