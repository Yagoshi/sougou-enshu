from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # 一般ユーザー用機能
    path('', views.main, name='main'),
    path('search_result/', views.searchResult, name='searchResult'),
    path('item/<int:item_id>/', views.itemDetail, name='itemDetail'),
    path('cart/', views.cart, name='cart'),
    path('add_to_cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/delete/<int:item_id>/', views.delete_cart, name='delete_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/commit/', views.checkoutCommit, name='checkoutCommit'),
    
    # 管理者用機能
    path('admin_main/', views.adminMain, name='adminMain'),
    path('admin_main/item/add/', views.adminItemAdd, name='adminItemAdd'),
    path('admin_main/item/edit/<int:item_id>/', views.adminItemEdit, name='adminItemEdit'),
    path('admin_main/item/delete/<int:item_id>/', views.adminItemDelete, name='adminItemDelete'),
    path('admin_main/item/toggle_recommend/<int:item_id>/', views.adminItemToggleRecommend, name='adminItemToggleRecommend'),
    
    # 追加：注文履歴とキャンセル機能
    path('admin_main/purchase/', views.adminPurchaseList, name='adminPurchaseList'),
    path('admin_main/purchase/cancel/<int:purchase_id>/', views.adminPurchaseCancel, name='adminPurchaseCancel'),

    path("item/<int:item_id>/review/", views.add_review, name="add_review"),
    path('items/<int:item_id>/chat/', views.itemChat, name='itemChat'),
]