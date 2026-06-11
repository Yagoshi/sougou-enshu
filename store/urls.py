from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.main, name='main'),
    path('search_result/', views.searchResult, name='searchResult'),
    path('item/<int:item_id>/', views.itemDetail, name='itemDetail'),
    path('cart/', views.cart, name='cart'),
    path('add_to_cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    
    # 追加：カートの更新・削除、購入処理
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/delete/<int:item_id>/', views.delete_cart, name='delete_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/commit/', views.checkoutCommit, name='checkoutCommit'),
]