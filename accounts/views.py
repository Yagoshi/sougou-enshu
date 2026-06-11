from django.shortcuts import render, redirect
from .models import User
from .forms import UserForm

def login(request):
    return render(request, 'accounts/login.html')

def userInfo(request):
    return render(request, 'accounts/userInfo.html')

def updateUser(request):
    return render(request, 'accounts/updateUser.html')

def updateUserConfirm(request):
    return render(request, 'accounts/updateUserConfirm.html')

def updateUserCommit(request):
    return render(request, 'accounts/updateUserCommit.html')

def withdrawConfirm(request):
    return render(request, 'accounts/withdrawConfirm.html')

def withdrawCommit(request):
    return render(request, 'accounts/withdrawCommit.html')

# 会員登録：入力画面 (M02)
def registerUser(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():  # 入力必須チェックがOKなら
            # データをセッションに一時保存して、確認画面へリダイレクト
            request.session['register_data'] = form.cleaned_data
            return redirect('accounts:registerUserConfirm')
    else:
        form = UserForm()
    
    return render(request, 'accounts/registerUser.html', {'form': form})

# 会員登録：確認画面 (M03)
def registerUserConfirm(request):
    # セッションからデータを取り出す
    data = request.session.get('register_data')
    if not data:
        return redirect('accounts:registerUser') # データがなければ入力画面へ戻す

    if request.method == 'POST':
        # 「登録する」ボタンが押されたら完了画面へ
        return redirect('accounts:registerUserCommit')

    return render(request, 'accounts/registerUserConfirm.html', {'data': data})

# 会員登録：完了処理 (M04)
def registerUserCommit(request):
    data = request.session.get('register_data')
    if not data:
        return redirect('accounts:registerUser')

    # ここで初めてデータベース(MySQL)に保存する
    User.objects.create(
        user_id=data['user_id'],
        password=data['password'],
        name=data['name'],
        address=data['address']
    )
    
    # 用が済んだセッションデータを削除
    del request.session['register_data']

    return render(request, 'accounts/registerUserCommit.html')