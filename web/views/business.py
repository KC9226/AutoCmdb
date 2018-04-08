#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.views import View
from django.shortcuts import render
from django.http import JsonResponse

from web.service import businessunit


class BusinessListView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'business_list.html')


class BusinessJsonView(View):
    def get(self, request):
        obj = businessunit.Business()
        response = obj.fetch_business(request)
        return JsonResponse(response.__dict__)

    def delete(self, request):
        response = businessunit.Business.delete_business(request)
        return JsonResponse(response.__dict__)

    def put(self, request):
        response = businessunit.Business.put_business(request)
        return JsonResponse(response.__dict__)

    def post(self, request, *args, **kwargs):
        response = businessunit.Business.post_business(request)
        # print(response.__dict__)
        return JsonResponse(response.__dict__)
        pass
