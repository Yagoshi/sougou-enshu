from django.test import TestCase
from django.urls import reverse
from store.models import Category, Item, ItemsInCart, Purchase
from accounts.models import User
from unittest.mock import patch, MagicMock


def create_test_data():
    category = Category.objects.create(category_id=1, name='テストカテゴリ')
    item = Item.objects.create(
        item_id=1, name='テスト商品', manufacturer='テストメーカー',
        color='赤', price=3000, stock=10, category=category,
    )
    user = User.objects.create(
        user_id='storeuser', password='pass1234',
        name='ストアテストユーザー', address='東京都1-1-1',
    )
    return category, item, user


class MainViewTest(TestCase):
    def test_main_page_returns_200(self):
        response = self.client.get(reverse('store:main'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/main.html')

    def test_main_page_shows_items(self):
        create_test_data()
        response = self.client.get(reverse('store:main'))
        self.assertContains(response, 'テスト商品')


class SearchViewTest(TestCase):
    def setUp(self):
        self.category, self.item, _ = create_test_data()

    def test_search_by_keyword(self):
        response = self.client.get(reverse('store:searchResult'), {'keyword': 'テスト'})
        self.assertContains(response, 'テスト商品')

    def test_search_no_results(self):
        response = self.client.get(reverse('store:searchResult'), {'keyword': '存在しない商品XYZ'})
        self.assertNotContains(response, 'テスト商品')


class CartViewTest(TestCase):
    def setUp(self):
        _, self.item, self.user = create_test_data()
        session = self.client.session
        session['login_user_id'] = self.user.user_id
        session.save()

    def test_cart_requires_login(self):
        self.client.session.flush()
        response = self.client.get(reverse('store:cart'))
        self.assertRedirects(response, reverse('accounts:login'))

    def test_add_to_cart(self):
        self.client.post(
            reverse('store:add_to_cart', args=[self.item.item_id]),
            {'amount': 2},
        )
        self.assertEqual(ItemsInCart.objects.filter(user=self.user).count(), 1)

    def test_delete_from_cart(self):
        ItemsInCart.objects.create(amount=1, item=self.item, user=self.user)
        self.client.post(reverse('store:delete_cart', args=[self.item.item_id]))
        self.assertFalse(ItemsInCart.objects.filter(user=self.user).exists())




class CheckoutViewTest(TestCase):
    def setUp(self):
        _, self.item, self.user = create_test_data()
        session = self.client.session
        session['login_user_id'] = self.user.user_id
        session.save()
        ItemsInCart.objects.create(amount=2, item=self.item, user=self.user)

    def _mock_payment_success(self):
        mock_res = MagicMock()
        mock_res.status_code = 200
        mock_res.json.return_value = {
            'status': 'succeeded',
            'transaction_id': 'test-txn-001',
            'card_last4': '4242',
        }
        return mock_res

    def test_checkout_commit_creates_purchase(self):
        with patch('store.views.requests.post', return_value=self._mock_payment_success()):
            self.client.post(reverse('store:checkoutCommit'), {
                'destination': '東京都港区1-1-1',
                'card_number': '4242424242424242',
            })
        self.assertTrue(Purchase.objects.filter(user=self.user).exists())

    def test_checkout_commit_reduces_stock(self):
        with patch('store.views.requests.post', return_value=self._mock_payment_success()):
            self.client.post(reverse('store:checkoutCommit'), {
                'destination': '東京都港区1-1-1',
                'card_number': '4242424242424242',
            })
        self.item.refresh_from_db()
        self.assertEqual(self.item.stock, 8)

    def test_checkout_commit_clears_cart(self):
        with patch('store.views.requests.post', return_value=self._mock_payment_success()):
            self.client.post(reverse('store:checkoutCommit'), {
                'destination': '東京都港区1-1-1',
                'card_number': '4242424242424242',
            })
        self.assertFalse(ItemsInCart.objects.filter(user=self.user).exists())