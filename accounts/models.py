from django.db import models
import random

class Coupon(models.Model):
    COUPON_CHOICES = [
        ('20%', '20% OFF'),
        ('50%', '50% OFF'),
        ('99%', '99% OFF'),
    ]

    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='coupons')
    coupon_type = models.CharField(max_length=3, choices=COUPON_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'account_coupons'

    def __str__(self):
        return f"{self.user.name} - {self.coupon_type}"

    @staticmethod
    def generate_coupon():
        """ランダムにクーポンを生成"""
        return random.choice(['20%', '50%', '99%'])
    
    
class User(models.Model):
    # varchar, 128桁, PK, INDEX, 自動採番なし
    user_id = models.CharField(max_length=128, primary_key=True, db_index=True)
    password = models.CharField(max_length=256)
    name = models.CharField(max_length=128)
    address = models.CharField(max_length=256)

    class Meta:
        # DBのテーブル名を指定
        db_table = 'account_user'

class Admin(models.Model):
    # varchar, 128桁, PK, INDEX, 自動採番なし
    admin_id = models.CharField(max_length=128, primary_key=True, db_index=True)
    password = models.CharField(max_length=256)

    class Meta:
        db_table = 'administrator_admin'