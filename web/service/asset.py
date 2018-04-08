#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
from django.db.models import Q
from repository import models
from utils.pager import PageInfo
from utils.response import BaseResponse
from django.http.request import QueryDict

from .base import BaseServiceList


class Asset(BaseServiceList):
    def __init__(self):
        # 查询条件的配置
        condition_config = [
            {'name': 'cabinet_num', 'text': '机柜号', 'condition_type': 'input'},
            {'name': 'device_type_id', 'text': '资产类型', 'condition_type': 'select', 'global_name': 'device_type_list'},
            {'name': 'device_status_id', 'text': '资产状态', 'condition_type': 'select',
             'global_name': 'device_status_list'},
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
                'q': 'device_type_id',
                'title': "资产类型",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@@device_type_list'}},
                'attr': {}
            },
            {
                'q': 'server_title',
                'title': "主机名",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@server_title'}},
                'attr': {}
            },
            {
                'q': 'network_title',
                'title': "网络设备标识",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@network_title'}},
                'attr': {}
            },
            {
                'q': 'idc_id',
                'title': "IDC",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@@idc_list'}},
                'attr': {'name': 'idc_id', 'id': '@idc_id', 'origin': '@idc_id', 'edit-enable': 'true',
                         'edit-type': 'select',
                         'global-name': 'idc_list'}
            },
            {
                'q': 'cabinet_num',
                'title': "机柜号",
                'display': 1,
                'text': {'content': "{cabinet_num}", 'kwargs': {'cabinet_num': '@cabinet_num'}},
                'attr': {'name': 'cabinet_num', 'edit-enable': 'true', 'edit-type': 'input', 'origin': '@cabinet_num', }
            },
            {
                'q': 'cabinet_order',
                'title': "位置",
                'display': 1,
                'text': {'content': "{cabinet_order}", 'kwargs': {'cabinet_order': '@cabinet_order'}},
                'attr': {'name': 'cabinet_order', 'edit-enable': 'true', 'edit-type': 'input',
                         'origin': '@cabinet_order', }
            },
            {
                'q': 'business_unit_id',
                'title': "业务线ID",
                'display': 0,
                'text': {'content': "", 'kwargs': {}},
                'attr': {}
            },
            {
                'q': 'business_unit__name',
                'title': "业务线",
                'display': 1,
                'text': {'content': "{business_unit__name}", 'kwargs': {'business_unit__name': '@business_unit__name'}},
                'attr': {'name': 'business_unit_id', 'id': '@business_unit_id', 'origin': '@business_unit_id',
                         'edit-enable': 'true',
                         'edit-type': 'select',
                         'global-name': 'business_unit_list'}
            },
            {
                'q': 'device_status_id',
                'title': "资产状态",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@@device_status_list'}},
                'attr': {'name': 'device_status_id', 'id': '@device_status_id', 'origin': '@device_status_id',
                         'edit-enable': 'true',
                         'edit-type': 'select',
                         'global-name': 'device_status_list'}
            },
            {
                'q': None,
                'title': "选项",
                'display': 1,
                'text': {
                    'content': "<a href='/asset-{device_type_id}-{nid}.html'>查看详细</a> | <a href='/edit-asset-{device_type_id}-{nid}.html'>编辑</a>",
                    'kwargs': {'device_type_id': '@device_type_id', 'nid': '@id'}},
                'attr': {}
            },
        ]
        # 额外搜索条件
        extra_select = {
            'server_title': 'SELECT hostname FROM repository_server WHERE repository_server.asset_id=repository_asset.id AND repository_asset.device_type_id=1',
            'network_title': 'SELECT manage_ip FROM repository_networkdevice WHERE repository_networkdevice.asset_id=repository_asset.id AND repository_asset.device_type_id=2',
        }
        super(Asset, self).__init__(condition_config, table_config, extra_select)

    @property
    def device_status_list(self):
        result = map(lambda x: {'id': x[0], 'name': x[1]}, models.Asset.device_status_choices)
        # print(list(result))
        return list(result)

    @property
    def device_type_list(self):
        result = map(lambda x: {'id': x[0], 'name': x[1]}, models.Asset.device_type_choices)
        # print(list(result))
        return list(result)

    @property
    def idc_list(self):
        values = models.IDC.objects.only('id', 'name', 'floor')
        print(values)
        result = map(lambda x: {'id': x.id, 'name': "%s-%s" % (x.name, x.floor)}, values)
        # print('idc_list', result, list(result))
        return list(result)

    @property
    def business_unit_list(self):
        values = models.BusinessUnit.objects.values('id', 'name')
        # print(list(values))
        return list(values)

    @staticmethod
    def assets_condition(request):
        con_str = request.GET.get('condition', None)
        # print(con_str, type(con_str))
        if not con_str:
            con_dict = {}
        else:
            con_dict = json.loads(con_str)
            # print(con_dict, type(con_dict))

        con_q = Q()
        for k, v in con_dict.items():
            temp = Q()
            temp.connector = 'OR'
            for item in v:
                temp.children.append((k, item))
            con_q.add(temp, 'AND')

        return con_q

    def fetch_assets(self, request):
        response = BaseResponse()
        try:
            ret = {}
            conditions = self.assets_condition(request)
            # print(conditions)
            asset_count = models.Asset.objects.filter(conditions).count()
            page_info = PageInfo(request.GET.get('pager', None), asset_count)
            print('values_list', self.values_list)
            asset_list = models.Asset.objects.filter(conditions).extra(select=self.extra_select).values(
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
                'device_status_list': self.device_status_list,
                'device_type_list': self.device_type_list,
                'idc_list': self.idc_list,
                'business_unit_list': self.business_unit_list
            }
            response.data = ret
            response.message = '获取成功'
        except Exception as e:
            response.status = False
            response.message = str(e)

        return response

    @staticmethod
    def delete_assets(request):
        response = BaseResponse()
        try:
            delete_dict = QueryDict(request.body, encoding='utf-8')
            id_list = delete_dict.getlist('id_list')
            models.Asset.objects.filter(id__in=id_list).delete()
            response.message = '删除成功'
        except Exception as e:
            response.status = False
            response.message = str(e)
        return response

    @staticmethod
    def put_assets(request):
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
                    models.Asset.objects.filter(id=nid).update(**row_dict)
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
    def post_assets(request):
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
                # response.data = models.Server.objects.filter(asset_id=asset_id).first()
                # tt = response.data.asset
                # print(type(response.data), response.data.asset.assetrecord_set.all())
                # print(type(response.data), response.data.asset.assetrecord_set.order_by('-id').all())
            else:
                response.data = models.NetworkDevice.objects.filter(asset_id=asset_id).select_related('asset').first()

        except Exception as e:
            response.status = False
            response.message = str(e)
        return response
