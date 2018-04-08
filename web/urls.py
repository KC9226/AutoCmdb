from django.conf.urls import url
from django.conf.urls import include
from django.contrib import admin
from web.views import account
from web.views import home
from web.views import asset
from web.views import user
from web.views import business

urlpatterns = [
    url(r'^login.html$', account.LoginView.as_view()),
    url(r'^logout.html$', account.LogoutView.as_view()),
    url(r'^index.html$', home.IndexView.as_view()),
    url(r'^cmdb.html$', home.CmdbView.as_view()),

    url(r'^asset.html$', asset.AssetListView.as_view()),
    url(r'^assets.html$', asset.AssetJsonView.as_view()),

    url(r'^idc.html$', asset.IDCListView.as_view()),
    url(r'^idcjson.html$', asset.IDCJsonView.as_view()),

    url(r'^asset-(?P<device_type_id>\d+)-(?P<asset_nid>\d+).html$', asset.AssetDetailView.as_view()),
    url(r'^add-asset.html$', asset.AddAssetView.as_view()),


    url(r'^users.html$', user.UserListView.as_view()),
    url(r'^userjson.html$', user.UserJsonView.as_view()),

    url(r'^business.html$', business.BusinessListView.as_view()),
    url(r'^businessjson.html$', business.BusinessJsonView.as_view()),

    url(r'^chart-(?P<chart_type>\w+).html$', home.ChartView.as_view()),
]