from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.defaults import page_not_found


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),       # storeアプリ（トップページ等）
    path('accounts/', include('accounts.urls')), # 追加：accountsアプリ
]
# 開発環境でメディアファイルを配信する設定
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # DEBUG=False でも開発サーバーで静的ファイルを配信する
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    

handler404 = 'django.views.defaults.page_not_found'

if settings.DEBUG:
    urlpatterns += [
        path('404/', lambda r: page_not_found(r, None)),
    ]