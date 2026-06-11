from django.db import models

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