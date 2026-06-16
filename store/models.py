from django.db import models

class Category(models.Model):
    # int, PK, INDEX, 自動採番なし
    category_id = models.IntegerField(primary_key=True, db_index=True)
    name = models.CharField(max_length=256)

    class Meta:
        db_table = 'shopping_category'

class Item(models.Model):
    # int, PK, INDEX, 自動採番なし
    item_id = models.IntegerField(primary_key=True, db_index=True)
    name = models.CharField(max_length=128)
    manufacturer = models.CharField(max_length=32)
    color = models.CharField(max_length=16)
    price = models.IntegerField()
    stock = models.IntegerField()
    recommended = models.BooleanField(default=False)
    image = models.ImageField(upload_to='items/', blank=True, null=True)
    
    # 外部キー制約 (DB上は category_id)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        db_table = 'shopping_item'

class ItemsInCart(models.Model):
    # int, PK, INDEX, 自動採番
    id = models.AutoField(primary_key=True, db_index=True)
    amount = models.IntegerField()
    # 登録日に現在日時を自動設定
    booked_date = models.DateTimeField(auto_now_add=True)
    
    # 外部キー制約
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    # accountsアプリのUserモデルを参照
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)

    class Meta:
        db_table = 'shopping_itemsincart'

class Purchase(models.Model):
    # int, PK, INDEX, 自動採番なし
    purchase_id = models.IntegerField(primary_key=True, db_index=True)
    destination = models.CharField(max_length=256)
    booked_date = models.DateTimeField(auto_now_add=True)
    cancel = models.BooleanField(default=False)
    
    # 決済API関連
    transaction_id = models.CharField(max_length=64, blank=True, null=True)
    payment_status = models.CharField(max_length=16, default='pending')
    card_last4 = models.CharField(max_length=4, blank=True, null=True)
    
    # 外部キー制約 (DB上は user_id)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)

    class Meta:
        db_table = 'shopping_purchase'

class PurchaseDetail(models.Model):
    # int, PK, INDEX, 自動採番なし
    purchase_detail_id = models.IntegerField(primary_key=True, db_index=True)
    # 1以上の整数を想定
    amount = models.IntegerField()
    
    # 外部キー制約 (DB上は item_id, purchase_id)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)

    class Meta:
        db_table = 'shopping_purchasedetail'