from django.contrib import admin
from .models import Category, Item, ItemsInCart, Purchase, PurchaseDetail

admin.site.register(Category)
admin.site.register(Item)
admin.site.register(ItemsInCart)
admin.site.register(Purchase)
admin.site.register(PurchaseDetail)