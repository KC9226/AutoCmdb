#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
from django.db.models import Q
from repository import models
from utils.pager import PageInfo
from utils.response import BaseResponse
from django.http.request import QueryDict

from .base import BaseServiceList


class Business(BaseServiceList):
    def __init__(self):
        # 查询条件的配置
        condition_config = [
            {'name': 'name', 'text': '业务线名称', 'condition_type': 'input'},
            {'name': 'contact_id', 'text': '业务联系人', 'condition_type': 'select', 'global_name': 'contact_id_list'},
            {'name': 'manager_id', 'text': '系统管理员', 'condition_type': 'select',
             'global_name': 'manager_id_list'},
        ]
        # 表格的配置
        table_config = [
            {
                'q': 'id',  # 用于数据库查询的字段，即Model.Tb.objects.filter(*[])
                'title': "ID",  # 前端表格中显示的标题
                'display': 1,  # 是否在前端显示，0表示在前端不显示, 1表示在前端隐藏, 2表示在前段显示
                'text': {'content': "{id}", 'kwargs': {'id': '@id'}},
                'attr': {'k1': 'v1'}  # 自定义属性
            },
            {
                'q': 'name',
                'title': "业务线名称",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@name'}},
                'attr': {'name': 'name', 'edit-enable': 'true', 'edit-type': 'input', 'origin': '@name', }
            },
            {
                'q': 'contact_id',
                'title': "业务联系人",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@@contact_id_list'}},
                'attr': {'name': 'contact_id', 'id': '@contact_id', 'origin': '@contact_id', 'edit-enable': 'true',
                         'edit-type': 'select',
                         'global-name': 'contact_id_list'}
            },
            {
                'q': 'manager_id',
                'title': "系统管理员",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@@manager_id_list'}},
                'attr': {'name': 'manager_id', 'id': '@manager_id', 'origin': '@manager_id', 'edit-enable': 'true',
                         'edit-type': 'select',
                         'global-name': 'manager_id_list'}
            },

            # {
            #     'q': 'business_unit_id',
            #     'title': "业务线ID",
            #     'display': 0,
            #     'text': {'content': "", 'kwargs': {}},
            #     'attr': {}
            # },

        ]
        # 额外搜索条件
        # extra_select = {
        #     'server_title': 'SELECT hostname FROM repository_server WHERE repository_server.asset_id=repository_asset.id AND repository_asset.device_type_id=1',
        #     'network_title': 'SELECT manage_ip FROM repository_networkdevice WHERE repository_networkdevice.asset_id=repository_asset.id AND repository_asset.device_type_id=2',
        # }
        extra_select = {}
        super(Business, self).__init__(condition_config, table_config, extra_select)

    @property
    def contact_id_list(self):
        values = models.UserGroup.objects.only('id', 'name')
        result = map(lambda x: {'id': x.id, 'name': x.name}, values)
        # print('idc_list', result, list(result))
        return list(result)

    @property
    def manager_id_list(self):
        values = models.UserGroup.objects.only('id', 'name')
        result = map(lambda x: {'id': x.id, 'name': x.name}, values)
        # print(list(values))
        return list(result)

    def fetch_business(self, request):
        response = BaseResponse()
        try:
            ret = {}
            conditions = self.assets_condition(request)
            # print(conditions)
            asset_count = models.BusinessUnit.objects.filter(conditions).count()
            page_info = PageInfo(request.GET.get('pager', None), asset_count)
            asset_list = models.BusinessUnit.objects.filter(conditions).extra(select=self.extra_select).values(
                *self.values_list)[page_info.start:page_info.end]
            # print(asset_list, type(asset_list))
            ret['table_config'] = self.table_config
            ret['condition_config'] = self.condition_config
            ret['data_list'] = list(asset_list)
            ret['page_info'] = {
                "page_str": page_info.pager(),
                "page_start": page_info.start,
            }
            ret['global_dict'] = {
                'contact_id_list': self.contact_id_list,
                'manager_id_list': self.manager_id_list,
            }
            response.data = ret
            response.message = '获取成功'
        except Exception as e:
            response.status = False
            response.message = str(e)

        return response

    @staticmethod
    def delete_business(request):
        response = BaseResponse()
        try:
            delete_dict = QueryDict(request.body, encoding='utf-8')
            id_list = delete_dict.getlist('id_list')
            models.BusinessUnit.objects.filter(id__in=id_list).delete()
            response.message = '删除成功'
        except Exception as e:
            response.status = False
            response.message = str(e)
        return response

    @staticmethod
    def put_business(request):
        response = BaseResponse()
        try:
            response.error = []
            put_dict = QueryDict(request.body, encoding='utf-8')
            # print('put_dict', put_dict)
            update_list = json.loads(put_dict.get('update_list'))
            # print('update_list', update_list)
            error_count = 0
            for row_dict in update_list:
                nid = row_dict.pop('nid')
                num = row_dict.pop('num')
                try:
                    models.BusinessUnit.objects.filter(id=nid).update(**row_dict)
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
    def post_business(request):
        response = BaseResponse()
        try:
            hostname = request.POST.get('hostname', None)
            manage_ip = request.POST.get('manage_ip', None)
            device_type_id = request.POST.get('device_type_id', None)
            device_status_id = request.POST.get('device_status_id', None)
            idc_id = request.POST.get('idc_id', None)
            business_unit_id = request.POST.get('business_unit_id', None)
            cabinet_num = request.POST.get('cabinet_num', None)
            cabinet_order = request.POST.get('cabinet_order', None)
            # add_dict = QueryDict(request.body, encoding='utf-8')
            # print('add_dict', add_dict)
            # print(hostname, manage_ip, device_type_id, device_status_id, idc_id, business_unit_id)
            obj_asset = models.Asset.objects.create(device_type_id=device_type_id, device_status_id=device_status_id,
                                                    cabinet_num=cabinet_num, cabinet_order=cabinet_order,
                                                    business_unit_id=business_unit_id, idc_id=idc_id)
            print('newobj_asset_id', obj_asset.id)
            if 1 == int(device_type_id):
                models.Server.objects.create(hostname=hostname, manage_ip=manage_ip, asset_id=obj_asset.id)
            elif 2 == int(device_type_id):
                models.NetworkDevice.objects.create(hostname=hostname, manage_ip=manage_ip, asset_id=obj_asset.id)
            if obj_asset:
                response.message = '添加资产成功'
            else:
                response.error = '添加资产失败'
        except Exception as e:
            response.status = False
            response.message = str(e)
        return response
        pass

    @staticmethod
    def assets_detail(device_type_id, asset_id):

        response = BaseResponse()
        try:
            if device_type_id == '1':
                response.data = models.Server.objects.filter(asset_id=asset_id).select_related('asset').first()
            else:
                response.data = models.NetworkDevice.objects.filter(asset_id=asset_id).select_related('asset').first()

        except Exception as e:
            response.status = False
            response.message = str(e)
        return response
