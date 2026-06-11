from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),       # storeアプリ（トップページ等）
    path('accounts/', include('accounts.urls')), # 追加：accountsアプリ
]