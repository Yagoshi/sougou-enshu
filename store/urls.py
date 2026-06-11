from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.main, name='main'),
    path('search_result/', views.searchResult, name='searchResult'),
    path('item/<int:item_id>/', views.itemDetail, name='itemDetail'),
    path('cart/', views.cart, name='cart'),
    path('add_to_cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
]