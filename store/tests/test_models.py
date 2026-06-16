from django.test import TestCase
from store.models import Category, Item, ItemsInCart, Purchase, PurchaseDetail
from accounts.models import User


class CategoryModelTest(TestCase):
    def test_category_create(self):
        category = Category.objects.create(category_id=1, name='家電')
        self.assertEqual(category.name, '家電')


class ItemModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(category_id=1, name='家電')

    def test_item_create(self):
        item = Item.objects.create(
            item_id=1, name='テストPC', manufacturer='テストメーカー',
            color='ブラック', price=100000, stock=10, category=self.category,
        )
        self.assertEqual(item.name, 'テストPC')
        self.assertEqual(item.price, 100000)

    def test_item_recommended_default_is_false(self):
        item = Item.objects.create(
            item_id=2, name='デフォルト商品', manufacturer='メーカー',
            color='白', price=5000, stock=5, category=self.category,
        )
        self.assertFalse(item.recommended)


class PurchaseModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(category_id=1, name='家電')
        self.item = Item.objects.create(
            item_id=1, name='購入商品', manufacturer='メーカー',
            color='黒', price=10000, stock=5, category=self.category,
        )
        self.user = User.objects.create(
            user_id='purchaseuser', password='pass1234',
            name='購入ユーザー', address='東京都1-1-1',
        )

    def test_purchase_create(self):
        purchase = Purchase.objects.create(
            purchase_id=1, destination='東京都渋谷区1-1-1', user=self.user,
        )
        self.assertFalse(purchase.cancel)

    def test_purchase_cancel_flag(self):
        purchase = Purchase.objects.create(
            purchase_id=2, destination='大阪府1-1-1', user=self.user,
        )
        purchase.cancel = True
        purchase.save()
        updated = Purchase.objects.get(purchase_id=2)
        self.assertTrue(updated.cancel)