from django import forms
from .models import Item

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        # テーブル定義書の全項目を対象にしちゃう
        fields = ['item_id', 'name', 'manufacturer', 'color', 'price', 'stock', 'recommended', 'category', 'image']
        labels = {
            'item_id': '商品ID (手動設定)',
            'name': '商品名',
            'manufacturer': 'メーカー名',
            'color': '商品の色',
            'price': '価格',
            'stock': '在庫数',
            'recommended': 'おすすめ商品指定 (チェックでTrue)',
            'category': 'カテゴリ',
            'image': '商品画像',
        }