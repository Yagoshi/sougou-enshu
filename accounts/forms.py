from django import forms
from .models import User

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        # 入力させる項目を指定
        fields = ['user_id', 'password', 'name', 'address']
        # パスワード入力欄を伏せ字（***）にする設定
        widgets = {
            'password': forms.PasswordInput(),
        }