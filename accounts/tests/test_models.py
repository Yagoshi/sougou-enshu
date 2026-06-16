from django.test import TestCase
from accounts.models import User, Admin


class UserModelTest(TestCase):
    """Userモデルのテスト"""

    def test_user_create(self):
        """ユーザーを正しく作成できること"""
        user = User.objects.create(
            user_id='testuser01',
            password='pass1234',
            name='テストユーザー',
            address='東京都千代田区1-1-1',
        )
        self.assertEqual(user.user_id, 'testuser01')
        self.assertEqual(user.name, 'テストユーザー')
        self.assertEqual(user.address, '東京都千代田区1-1-1')

    def test_user_pk_is_user_id(self):
        """主キーがuser_idであること"""
        user = User.objects.create(
            user_id='pktest01',
            password='pass1234',
            name='PKテスト',
            address='大阪府大阪市1-1-1',
        )
        found = User.objects.get(pk='pktest01')
        self.assertEqual(found.user_id, user.user_id)

    def test_user_id_unique(self):
        """同じuser_idで2件登録するとエラーになること"""
        User.objects.create(
            user_id='dupuser',
            password='pass1234',
            name='重複テスト',
            address='北海道札幌市1-1-1',
        )
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            User.objects.create(
                user_id='dupuser',
                password='pass9999',
                name='重複テスト2',
                address='北海道函館市2-2-2',
            )


class AdminModelTest(TestCase):
    """Adminモデルのテスト"""

    def test_admin_create(self):
        """管理者を正しく作成できること"""
        from django.contrib.auth.hashers import make_password
        admin = Admin.objects.create(
            admin_id='admin01',
            password=make_password('adminpass'),
        )
        self.assertEqual(admin.admin_id, 'admin01')

    def test_admin_password_is_hashed(self):
        """管理者パスワードがハッシュ化されて保存されること"""
        from django.contrib.auth.hashers import make_password, check_password
        raw_password = 'adminpass'
        admin = Admin.objects.create(
            admin_id='admin02',
            password=make_password(raw_password),
        )
        self.assertNotEqual(admin.password, raw_password)
        self.assertTrue(check_password(raw_password, admin.password))