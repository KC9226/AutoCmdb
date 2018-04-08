#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
from django.views import View
from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.http import JsonResponse

from web.service import asset
from web.service.idc_service import IdcService


class AssetListView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'asset_list.html')


class AssetJsonView(View):
    def get(self, request):
        obj = asset.Asset()
        response = obj.fetch_assets(request)
        return JsonResponse(response.__dict__)

    def delete(self, request):
        response = asset.Asset.delete_assets(request)
        return JsonResponse(response.__dict__)

    def put(self, request):
        response = asset.Asset.put_assets(request)
        return JsonResponse(response.__dict__)


class AssetDetailView(View):
    def get(self, request, device_type_id, asset_nid):
        response = asset.Asset.assets_detail(device_type_id, asset_nid)
        # res1 = response.data.asset.assetrecord_set.order_by('-id').all()
        # print('response1', res1)
        # return render(request, 'asset_detail.html', {'response': response, 'response1 ': list(res1), 'device_type_id': device_type_id})
        return render(request, 'asset_detail.html', {'response': response, 'device_type_id': device_type_id})


class AddAssetView(View):
    def get(self, request, *args, **kwargs):
        obj = asset.Asset()
        return render(request, 'add_asset.html', {'device_status_list': obj.device_status_list,
                                                  'device_type_list': obj.device_type_list,
                                                  'idc_list': obj.idc_list,
                                                  'business_unit_list': obj.business_unit_list
                                                  })

    def post(self, request, *args, **kwargs):
        response = asset.Asset.post_assets(request)
        # print(response.__dict__)
        return JsonResponse(response.__dict__)
        pass


class IDCListView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'idc_list.html')


class IDCJsonView(View):
    def get(self, request):

        obj = IdcService()
        response = obj.fetch_idc(request)
        return HttpResponse(json.dumps(response.__dict__))

    def delete(self, request):
        response = IdcService.delete_idc(request)
        return JsonResponse(response.__dict__)
        pass

    def put(self, request):
        response = IdcService.put_idc(request)
        return JsonResponse(response.__dict__)
        pass

    def post(self, request, *args, **kwargs):
        response = IdcService.post_idc(request)
        # print(response.__dict__)
        return JsonResponse(response.__dict__)
        pass

