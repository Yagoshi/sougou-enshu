from django.test import TestCase
from accounts.forms import UserForm, UserUpdateForm
from accounts.models import User


class UserFormTest(TestCase):
    """会員登録フォーム (UserForm) のテスト"""

    def _valid_data(self, **overrides):
        data = {
            'user_id': 'formuser01',
            'password': 'pass1234',
            'password_confirm': 'pass1234',
            'name': 'フォームテスト太郎',
            'address': '東京都新宿区1-1-1',
        }
        data.update(overrides)
        return data

    def test_valid_form(self):
        """正しいデータを入力するとis_validがTrueになること"""
        form = UserForm(data=self._valid_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_without_user_id(self):
        """user_idが空だとis_validがFalseになること"""
        form = UserForm(data=self._valid_data(user_id=''))
        self.assertFalse(form.is_valid())
        self.assertIn('user_id', form.errors)

    def test_invalid_without_password(self):
        """passwordが空だとis_validがFalseになること"""
        form = UserForm(data=self._valid_data(password=''))
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)

    def test_invalid_when_passwords_do_not_match(self):
        """パスワードと確認用パスワードが不一致だとis_validがFalseになること"""
        form = UserForm(data=self._valid_data(password_confirm='wrong_pass'))
        self.assertFalse(form.is_valid())
        self.assertIn('password_confirm', form.errors)

    def test_invalid_without_name(self):
        """nameが空だとis_validがFalseになること"""
        form = UserForm(data=self._valid_data(name=''))
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_invalid_without_address(self):
        """addressが空だとis_validがFalseになること"""
        form = UserForm(data=self._valid_data(address=''))
        self.assertFalse(form.is_valid())
        self.assertIn('address', form.errors)

    def test_invalid_duplicate_user_id(self):
        """既存のuser_idで登録するとis_validがFalseになること"""
        User.objects.create(
            user_id='dupuser', password='pass1234',
            name='既存ユーザー', address='東京都渋谷区1-1-1',
        )
        form = UserForm(data=self._valid_data(user_id='dupuser'))
        self.assertFalse(form.is_valid())
        self.assertIn('user_id', form.errors)


class UserUpdateFormTest(TestCase):
    """会員情報更新フォーム (UserUpdateForm) のテスト"""

    def setUp(self):
        self.user = User.objects.create(
            user_id='updateuser01', password='pass1234',
            name='更新前ユーザー', address='東京都港区1-1-1',
        )

    def test_valid_form_without_password_change(self):
        """パスワード変更なしでも有効なこと"""
        form = UserUpdateForm(
            data={'name': '更新後', 'address': '東京都品川区2-2-2',
                  'new_password': '', 'new_password_confirm': ''},
            instance=self.user,
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_valid_form_with_password_change(self):
        """新パスワードと確認が一致していれば有効なこと"""
        form = UserUpdateForm(
            data={'name': '更新後', 'address': '東京都品川区2-2-2',
                  'new_password': 'newpass1234', 'new_password_confirm': 'newpass1234'},
            instance=self.user,
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_when_new_passwords_do_not_match(self):
        """新パスワードと確認が不一致だとis_validがFalseになること"""
        form = UserUpdateForm(
            data={'name': '更新後', 'address': '東京都品川区2-2-2',
                  'new_password': 'newpass1234', 'new_password_confirm': 'different'},
            instance=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('new_password_confirm', form.errors)