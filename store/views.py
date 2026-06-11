from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, Category, ItemsInCart
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