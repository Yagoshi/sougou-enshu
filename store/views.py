from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Max  # IDの自動採番に必要
from django.db import transaction # 在庫減算と注文処理を安全に行うために必要
from .models import Item, Category, ItemsInCart, Purchase, PurchaseDetail
from accounts.models import User

# 商品検索・一覧画面 (S01)
def main(request):
    items = Item.objects.all()
    categories = Category.objects.all()
    
    context = {
        'items': items,
        'categories': categories,
    }
    return render(request, 'store/main.html', context)

# 検索結果画面 (S02)
def searchResult(request):
    keyword = request.GET.get('keyword')
    category_id = request.GET.get('category')

    results = Item.objects.all()

    if keyword:
        results = results.filter(name__icontains=keyword)

    if category_id:
        results = results.filter(category_id=category_id)

    context = {
        'results': results,
        'keyword': keyword,
    }
    return render(request, 'store/searchResult.html', context)

# 商品詳細画面 (S03)
def itemDetail(request, item_id):
    item = get_object_or_404(Item, item_id=item_id)
    context = {
        'item': item
    }
    return render(request, 'store/itemDetail.html', context)

# ショッピングカート画面 (S04)
def cart(request):
    # セッションからログインユーザーを取得
    user_id = request.session.get('login_user_id')
    if not user_id:
        return redirect('accounts:login')
        
    user = get_object_or_404(User, user_id=user_id)
    
    # このユーザーのカートに入っている商品を全て取得
    cart_items = ItemsInCart.objects.filter(user=user)
    
    # 合計金額を計算
    total_price = sum(item.item.price * item.amount for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'store/cart.html', context)

# カートに追加する処理（画面表示はせず、処理が終わったらcartへリダイレクト）
def add_to_cart(request, item_id):
    if request.method == 'POST':
        user_id = request.session.get('login_user_id')
        
        if not user_id:
            return redirect('accounts:login')
            
        # フォームから送信された数量を取得（デフォルト1）
        amount = int(request.POST.get('amount', 1))
        
        item = get_object_or_404(Item, item_id=item_id)
        user = get_object_or_404(User, user_id=user_id)
        
        # カートに既に同じ商品があれば数量を加算、なければ新規作成
        cart_item, created = ItemsInCart.objects.get_or_create(
            user=user,
            item=item,
            defaults={'amount': amount}
        )
        if not created:
            cart_item.amount += amount
            cart_item.save()
            
        return redirect('store:cart')

# カート内の数量変更
def update_cart(request, item_id):
    user_id = request.session.get('login_user_id')
    if not user_id: return redirect('accounts:login')
    if request.method == 'POST':
        amount = int(request.POST.get('amount', 1))
        user = get_object_or_404(User, user_id=user_id)
        item = get_object_or_404(Item, item_id=item_id)
        cart_item = get_object_or_404(ItemsInCart, user=user, item=item)
        
        # 在庫数を超えない範囲で更新
        if amount > 0 and amount <= item.stock:
            cart_item.amount = amount
            cart_item.save()
    return redirect('store:cart')

# カートから商品を削除
def delete_cart(request, item_id):
    user_id = request.session.get('login_user_id')
    if not user_id: return redirect('accounts:login')
    user = get_object_or_404(User, user_id=user_id)
    item = get_object_or_404(Item, item_id=item_id)
    # カートから該当レコードを削除
    ItemsInCart.objects.filter(user=user, item=item).delete()
    return redirect('store:cart')

# 購入確認画面 (S05)
def checkout(request):
    user_id = request.session.get('login_user_id')
    if not user_id: return redirect('accounts:login')
    
    user = get_object_or_404(User, user_id=user_id)
    cart_items = ItemsInCart.objects.filter(user=user)
    
    if not cart_items: return redirect('store:cart')
    
    total_price = sum(item.item.price * item.amount for item in cart_items)
    context = {
        'user': user,
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'store/checkout.html', context)

# 購入完了処理 (S06)
def checkoutCommit(request):
    user_id = request.session.get('login_user_id')
    if not user_id: return redirect('accounts:login')
    if request.method != 'POST': return redirect('store:cart')

    # 送信された配送先（変更されていればその値）を取得
    destination = request.POST.get('destination')
    user = get_object_or_404(User, user_id=user_id)
    cart_items = ItemsInCart.objects.filter(user=user)
    
    if not cart_items: return redirect('store:cart')

    # transaction.atomic() で囲むことで、途中でエラーが起きたら全てのDB操作をキャンセルする
    with transaction.atomic():
        # 在庫不足チェック
        for c_item in cart_items:
            if c_item.amount > c_item.item.stock:
                return redirect('store:cart') # 実際の運用ではエラー画面を出しますが今回はカートに戻します

        # PurchaseのIDを手動採番 (現在の最大値+1)
        max_p = Purchase.objects.aggregate(Max('purchase_id'))['purchase_id__max']
        next_p_id = (max_p or 0) + 1
        
        # 注文テーブル(Purchase)に保存
        purchase = Purchase.objects.create(
            purchase_id=next_p_id,
            destination=destination,
            user=user
        )

        # PurchaseDetailのIDを手動採番
        max_pd = PurchaseDetail.objects.aggregate(Max('purchase_detail_id'))['purchase_detail_id__max']
        next_pd_id = (max_pd or 0) + 1

        # カートの中身をループして、注文詳細(PurchaseDetail)への保存と在庫減算を実行
        for c_item in cart_items:
            PurchaseDetail.objects.create(
                purchase_detail_id=next_pd_id,
                amount=c_item.amount,
                item=c_item.item,
                purchase=purchase
            )
            next_pd_id += 1
            
            # 商品テーブルの在庫を減らす
            c_item.item.stock -= c_item.amount
            c_item.item.save()

        # 購入が完了したのでカートを空にする
        cart_items.delete()

    return render(request, 'store/purchaseComplete.html')