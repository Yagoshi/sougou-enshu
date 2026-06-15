from django import forms
from .models import User

# 会員登録用フォーム (M02用)
class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''
    class Meta:
        model = User
        fields = ['user_id', 'password', 'name', 'address']
        widgets = {
            'password': forms.PasswordInput(),
        }
        labels = {
            'user_id': 'ユーザーID',
            'password': 'パスワード',
            'name': '名前',
            'address': '住所',
        }

# 会員情報更新用フォーム (M06用)
class UserUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''
    class Meta:
        model = User
        # 更新できるのは名前と住所のみに制限
        fields = ['name', 'address']

