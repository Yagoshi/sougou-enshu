from django.test import TestCase
from django.urls import reverse
from accounts.models import User, Admin
from django.contrib.auth.hashers import make_password


class LoginViewTest(TestCase):
    """会員ログイン画面のテスト"""

    def setUp(self):
        self.user = User.objects.create(
            user_id='loginuser', password=make_password('pass1234'),
            name='ログインテスト', address='東京都1-1-1',
        )

    def test_login_page_returns_200(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_login_success_redirects_to_main(self):
        response = self.client.post(reverse('accounts:login'), {
            'user_id': 'loginuser', 'password': 'pass1234',
        })
        self.assertRedirects(response, reverse('store:main'))

    def test_login_sets_session(self):
        self.client.post(reverse('accounts:login'), {
            'user_id': 'loginuser', 'password': 'pass1234',
        })
        self.assertEqual(self.client.session.get('login_user_id'), 'loginuser')

    def test_login_fail_with_wrong_password(self):
        response = self.client.post(reverse('accounts:login'), {
            'user_id': 'loginuser', 'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '間違っています')


class RegisterViewTest(TestCase):
    """会員登録フローのテスト"""

    def test_register_page_returns_200(self):
        response = self.client.get(reverse('accounts:registerUser'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/registerUser.html')

    def test_register_commit_creates_user(self):
        session = self.client.session
        session['register_data'] = {
            'user_id': 'newuser02', 'password': 'pass1234',
            'name': '新規ユーザー2', 'address': '大阪府1-1-1',
        }
        session.save()
        self.client.post(reverse('accounts:registerUserCommit'))
        self.assertTrue(User.objects.filter(user_id='newuser02').exists())


class LogoutViewTest(TestCase):
    """ログアウトのテスト"""

    def test_logout_clears_session(self):
        session = self.client.session
        session['login_user_id'] = 'someuser'
        session.save()
        self.client.get(reverse('accounts:logout'))
        self.assertIsNone(self.client.session.get('login_user_id'))


class UserInfoViewTest(TestCase):
    """会員情報確認画面のテスト"""

    def setUp(self):
        self.user = User.objects.create(
            user_id='infouser', password='pass1234',
            name='情報確認ユーザー', address='東京都1-1-1',
        )

    def test_user_info_requires_login(self):
        response = self.client.get(reverse('accounts:userInfo'))
        self.assertRedirects(response, reverse('accounts:login'))

    def test_user_info_returns_200_when_logged_in(self):
        session = self.client.session
        session['login_user_id'] = 'infouser'
        session.save()
        response = self.client.get(reverse('accounts:userInfo'))
        self.assertEqual(response.status_code, 200)


class WithdrawViewTest(TestCase):
    """退会フローのテスト"""

    def setUp(self):
        self.user = User.objects.create(
            user_id='withdrawuser', password='pass1234',
            name='退会テスト', address='東京都1-1-1',
        )
        session = self.client.session
        session['login_user_id'] = 'withdrawuser'
        session.save()

    def test_withdraw_commit_deletes_user(self):
        self.client.post(reverse('accounts:withdrawCommit'))
        self.assertFalse(User.objects.filter(user_id='withdrawuser').exists())


class AdminLoginViewTest(TestCase):
    """管理者ログインのテスト"""

    def setUp(self):
        Admin.objects.create(
            admin_id='admin01', password=make_password('adminpass'),
        )

    def test_admin_login_page_returns_200(self):
        response = self.client.get(reverse('accounts:adminLogin'))
        self.assertEqual(response.status_code, 200)

    def test_admin_login_fail_wrong_password(self):
        response = self.client.post(reverse('accounts:adminLogin'), {
            'admin_id': 'admin01', 'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '間違っています')