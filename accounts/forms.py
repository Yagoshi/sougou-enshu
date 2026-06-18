from django import forms
from .models import User

# 会員登録用フォーム (M02用)
class UserForm(forms.ModelForm):
    password_confirm = forms.CharField(
        label='パスワード（確認）',
        widget=forms.PasswordInput(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''

        self.order_fields([
            'user_id',
            'password',
            'password_confirm',
            'name',
            'address',
        ])

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

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'パスワードが一致しません。')

        return cleaned_data

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'パスワードが一致しません。')
        return cleaned_data

# 会員情報更新用フォーム (M06用)
class UserUpdateForm(forms.ModelForm):
    new_password = forms.CharField(
        label='新しいパスワード',
        widget=forms.PasswordInput(),
        required=False,
    )
    new_password_confirm = forms.CharField(
        label='新しいパスワード（確認）',
        widget=forms.PasswordInput(),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''

    class Meta:
        model = User
        fields = ['name', 'address']

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        new_password_confirm = cleaned_data.get('new_password_confirm')
        if new_password and new_password != new_password_confirm:
            self.add_error('new_password_confirm', '新しいパスワードが一致しません。')
        return cleaned_data
