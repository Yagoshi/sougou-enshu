from django import forms
from .models import Item
from .models import Review

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


class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [
        (5, "★★★★★ とても良い"),
        (4, "★★★★☆ 良い"),
        (3, "★★★☆☆ 普通"),
        (2, "★★☆☆☆ 悪い"),
        (1, "★☆☆☆☆ とても悪い"),
    ]

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect,
        label="評価"
    )

    class Meta:
        model = Review
        fields = ["rating", "title", "comment"]

        labels = {
            "title": "レビュータイトル",
            "comment": "レビュー本文",
        }

        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "例：とても使いやすい商品です"
            }),
            "comment": forms.Textarea(attrs={
                "placeholder": "商品の感想を入力してください",
                "rows": 5
            }),
        }