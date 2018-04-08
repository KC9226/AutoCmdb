#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
from django.db.models import Q
from repository import models
from utils.pager import PageInfo
from utils.response import BaseResponse
from django.http.request import QueryDict

from .base import BaseServiceList


class IdcService(BaseServiceList):
    def __init__(self):
        # 查询条件的配置
        condition_config = [
            {'name': 'name', 'text': 'IDC名称', 'condition_type': 'input'},
            {'name': 'email', 'text': '楼层', 'condition_type': 'input'},
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
                'title': "机房",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@name'}},
                'attr': {'name': 'name', 'origin': '@name', 'edit-enable': 'true', 'edit-type': 'input'}
            },
            {
                'q': 'floor',
                'title': "楼层",
                'display': 1,
                'text': {'content': "{n}", 'kwargs': {'n': '@floor'}},
                'attr': {'name': 'floor', 'origin': '@floor', 'edit-enable': 'true', 'edit-type': 'input'}
            },
        ]
        # 额外搜索条件
        extra_select = {}
        super(IdcService, self).__init__(condition_config, table_config, extra_select)

    def fetch_idc(self, request):
        response = BaseResponse()
        try:
            ret = {}
            conditions = self.assets_condition(request)

            asset_count = models.IDC.objects.filter(conditions).count()
            page_info = PageInfo(request.GET.get('pager', None), asset_count)

            asset_list = models.IDC.objects.filter(conditions).extra(select=self.extra_select).values(
                *self.values_list)[page_info.start:page_info.end]

            ret['table_config'] = self.table_config
            ret['condition_config'] = self.condition_config
            ret['data_list'] = list(asset_list)
            ret['page_info'] = {
                "page_str": page_info.pager(),
                "page_start": page_info.start,
            }
            ret['global_dict'] = {}
            response.data = ret
            response.message = '获取成功'
        except Exception as e:
            response.status = False
            response.message = str(e)

        return response

    @staticmethod
    def delete_idc(request):
        response = BaseResponse()
        try:
            delete_dict = QueryDict(request.body, encoding='utf-8')
            id_list = delete_dict.getlist('id_list')
            models.IDC.objects.filter(id__in=id_list).delete()
            response.message = '删除成功'
            pass
        except Exception as e:
            response.status = False
            response.message = str(e)
        return response

    @staticmethod
    def put_idc(request):
        response = BaseResponse()
        try:
            response.error = []
            put_dict = QueryDict(request.body, encoding='utf-8')
            update_list = json.loads(put_dict.get('update_list'))
            print('updatelist', update_list)
            error_count = 0
            for row_dict in update_list:
                nid = row_dict.pop('nid')
                num = row_dict.pop('num')
                try:
                    models.IDC.objects.filter(id=nid).update(**row_dict)
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
    def post_idc(request):
        response = BaseResponse()
        try:
            name = request.POST.get('name', None)
            floor = request.POST.get('floor', None)
            # add_dict = QueryDict(request.body, encoding='utf-8')
            # print('add_dict', add_dict)
            # print(hostname, manage_ip, device_type_id, device_status_id, idc_id, business_unit_id)
            t_dict = {'name': name, 'floor': floor}
            print(t_dict)
            error_count = 0
            idc_obj = models.IDC.objects.filter(**t_dict)
            if idc_obj:
                response.message = '添加的IDC信息已经存在'
                response.status = False
                response.error = '错误代码1'
                pass
            else:
                try:
                    models.IDC.objects.create(name=name, floor=floor)
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