from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Admin 
from .forms import UserForm, UserUpdateForm
from store.models import Purchase, PurchaseDetail

# 会員ログイン画面 (M01)
def login(request):
    error_message = ''
    if request.method == 'POST':
        input_user_id = request.POST.get('user_id')
        input_password = request.POST.get('password')
        try:
            user = User.objects.get(user_id=input_user_id, password=input_password)
            request.session['login_user_id'] = user.user_id
            return redirect('store:main')
        except User.DoesNotExist:
            error_message = '会員IDまたはパスワードが間違っています。'
    return render(request, 'accounts/login.html', {'error_message': error_message})

# 会員登録 (M02)
def registerUser(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            request.session['register_data'] = form.cleaned_data
            return redirect('accounts:registerUserConfirm')
    else:
        form = UserForm()
    return render(request, 'accounts/registerUser.html', {'form': form})

# 会員登録確認 (M03)
def registerUserConfirm(request):
    data = request.session.get('register_data')
    if not data:
        return redirect('accounts:registerUser')
    if request.method == 'POST':
        return redirect('accounts:registerUserCommit')
    return render(request, 'accounts/registerUserConfirm.html', {'data': data})

# 会員登録完了 (M04)
def registerUserCommit(request):
    data = request.session.get('register_data')
    if not data:
        return redirect('accounts:registerUser')
    User.objects.create(
        user_id=data['user_id'],
        password=data['password'],
        name=data['name'],
        address=data['address']
    )
    del request.session['register_data']
    return render(request, 'accounts/registerUserCommit.html')

# 会員情報確認画面 (M05) - 履歴取得機能を追加
def userInfo(request):
    user_id = request.session.get('login_user_id')
    if not user_id:
        return redirect('accounts:login')
    
    user = get_object_or_404(User, user_id=user_id)

    # このユーザーの注文履歴を取得（最新の注文が上に来るように -booked_date を指定）
    purchases = Purchase.objects.filter(user=user).order_by('-booked_date')

    # テンプレートで表示しやすいように、各注文に紐づく詳細と合計金額をリスト化して渡す
    purchase_history = []
    for purchase in purchases:
        details = PurchaseDetail.objects.filter(purchase=purchase)
        # 注文ごとの合計金額を計算
        total_price = sum(detail.item.price * detail.amount for detail in details)
        
        purchase_history.append({
            'purchase': purchase,
            'details': details,
            'total_price': total_price
        })

    return render(request, 'accounts/userInfo.html', {
        'user': user,
        'purchase_history': purchase_history
    })

# 会員情報更新画面 (M06)
def updateUser(request):
    user_id = request.session.get('login_user_id')
    if not user_id:
        return redirect('accounts:login')
    
    user = get_object_or_404(User, user_id=user_id)
    
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            request.session['update_data'] = form.cleaned_data
            return redirect('accounts:updateUserConfirm')
    else:
        form = UserUpdateForm(instance=user)

    return render(request, 'accounts/updateUser.html', {'form': form})

# 会員情報更新確認画面 (M07)
def updateUserConfirm(request):
    user_id = request.session.get('login_user_id')
    if not user_id:
        return redirect('accounts:login')

    data = request.session.get('update_data')
    if not data:
        return redirect('accounts:updateUser')

    if request.method == 'POST':
        return redirect('accounts:updateUserCommit')

    return render(request, 'accounts/updateUserConfirm.html', {'data': data})

# 会員情報更新完了画面 (M08)
def updateUserCommit(request):
    user_id = request.session.get('login_user_id')
    if not user_id:
        return redirect('accounts:login')

    data = request.session.get('update_data')
    if not data:
        return redirect('accounts:updateUser')

    user = get_object_or_404(User, user_id=user_id)
    user.name = data['name']
    user.address = data['address']
    user.save()

    del request.session['update_data']
    return render(request, 'accounts/updateUserCommit.html')

# 退会確認画面 (M09)
def withdrawConfirm(request):
    user_id = request.session.get('login_user_id')
    if not user_id:
        return redirect('accounts:login')

    if request.method == 'POST':
        return redirect('accounts:withdrawCommit')

    return render(request, 'accounts/withdrawConfirm.html')

# 退会完了画面 (M10)
def withdrawCommit(request):
    user_id = request.session.get('login_user_id')
    if not user_id:
        return redirect('accounts:login')

    user = get_object_or_404(User, user_id=user_id)
    user.delete()
    request.session.flush()

    return render(request, 'accounts/withdrawCommit.html')


# 管理者ログイン画面
def adminLogin(request):
    error_message = ''
    if request.method == 'POST':
        input_admin_id = request.POST.get('admin_id')
        input_password = request.POST.get('password')
        try:
            # データベースから管理者を検索
            admin = Admin.objects.get(admin_id=input_admin_id, password=input_password)
            # 成功したら管理者用セッションを発行
            request.session['admin_login_id'] = admin.admin_id
            return redirect('store:adminMain')
        except Admin.DoesNotExist:
            error_message = '管理者IDまたはパスワードが間違っています。'
            
    return render(request, 'accounts/adminLogin.html', {'error_message': error_message})

# 会員ログアウト
def logout(request):
    request.session.flush()
    return redirect('store:main')

# 購入履歴画面
def purchaseHistory(request):
    user_id = request.session.get('login_user_id')
    if not user_id:
        return redirect('accounts:login')

    user = get_object_or_404(User, user_id=user_id)
    purchases = Purchase.objects.filter(user=user).order_by('-booked_date')

    purchase_history = []
    for purchase in purchases:
        details = PurchaseDetail.objects.filter(purchase=purchase)
        total_price = sum(detail.item.price * detail.amount for detail in details)
        purchase_history.append({
            'purchase': purchase,
            'details': details,
            'total_price': total_price
        })

    return render(request, 'accounts/purchaseHistory.html', {
        'purchase_history': purchase_history
    })