from django.test import TestCase
from store.forms import ItemForm
from store.models import Category


class ItemFormTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(category_id=1, name='テストカテゴリ')

    def _valid_data(self, **overrides):
        data = {
            'item_id': 100, 'name': 'テスト商品', 'manufacturer': 'テストメーカー',
            'color': '黒', 'price': 5000, 'stock': 10,
            'recommended': False, 'category': self.category.category_id,
        }
        data.update(overrides)
        return data

    def test_valid_form(self):
        form = ItemForm(data=self._valid_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_without_name(self):
        form = ItemForm(data=self._valid_data(name=''))
        self.assertFalse(form.is_valid())

    def test_invalid_without_price(self):
        form = ItemForm(data=self._valid_data(price=''))
        self.assertFalse(form.is_valid())

    def test_invalid_price_not_integer(self):
        form = ItemForm(data=self._valid_data(price='五千円'))
        self.assertFalse(form.is_valid())