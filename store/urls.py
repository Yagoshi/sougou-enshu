from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.main, name='main'), # S01
    path('search_result/', views.searchResult, name='searchResult'), # S02
    path('item/<int:item_id>/', views.itemDetail, name='itemDetail'), # S03
    path('cart/', views.cart, name='cart'), # S04
]