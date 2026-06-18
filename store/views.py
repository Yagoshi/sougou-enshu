import os
import requests
import google.generativeai as genai
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Max
from django.db import transaction
from .models import Item, Category, ItemsInCart, Purchase, PurchaseDetail, Review
from accounts.models import User
from .forms import ItemForm
from django.contrib.auth.decorators import login_required
from accounts.models import Coupon, User
import random

from django.db.models import Avg
from .forms import ReviewForm


def main(request):
    from django.db.models import Avg, Count, Min, Max
    items = Item.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    )
    categories = Category.objects.all()
    price_min = Item.objects.aggregate(Min('price'))['price__min'] or 0
    price_max = Item.objects.aggregate(Max('price'))['price__max'] or 100000
    context = {
        'items': items,
        'categories': categories,
        'min_price': price_min,
        'max_price': price_max,
    }
    if request.session.get('login_user_id', None):
        user_id = request.session.get('login_user_id', None)
        user = User.objects.get(user_id=user_id)
        context["user"] = user
    return render(request, 'store/main.html', context)

def searchResult(request):
    from django.db.models import Avg, Count, Min, Max
    keyword = request.GET.get('keyword')
    category_id = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    results = Item.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    )

    if keyword:
        results = results.filter(name__icontains=keyword)
    if category_id:
        results = results.filter(category_id=category_id)
    if min_price:
        results = results.filter(price__gte=int(min_price))
    if max_price:
        results = results.filter(price__lte=int(max_price))

    price_min = Item.objects.aggregate(Min('price'))['price__min'] or 0
    price_max = Item.objects.aggregate(Max('price'))['price__max'] or 100000

    context = {
        'results': results,
        'keyword': keyword,
        'categories': Category.objects.all(),
        'min_price': price_min,
        'max_price': price_max,
        'selected_min': int(min_price) if min_price else price_min,
        'selected_max': int(max_price) if max_price else price_max,
    }
    return render(request, 'store/searchResult.html', context)

def itemDetail(request, item_id):
    item = get_object_or_404(Item, item_id=item_id)

    reviews = Review.objects.filter(item=item).select_related("user")

    review_count = reviews.count()

    avg_rating = reviews.aggregate(
        avg=Avg("rating")
    )["avg"]

    if avg_rating is None:
        avg_rating = 0

    rating_distribution = []

    for star in range(5, 0, -1):
        count = reviews.filter(rating=star).count()

        if review_count > 0:
            percent = round((count / review_count) * 100)
        else:
            percent = 0

        rating_distribution.append({
            "star": star,
            "count": count,
            "percent": percent,
        })

    form = ReviewForm()

    context = {
        "item": item,
        "reviews": reviews,
        "review_count": review_count,
        "avg_rating": round(avg_rating, 1),
        "rating_distribution": rating_distribution,
        "form": form,
        "login_user_id": request.session.get("login_user_id"),
    }

    return render(request, "store/itemDetail.html", context)

def cart(request):
    user_id = request.session.get('login_user_id')
    if not user_id: return redirect('accounts:login')
    user = get_object_or_404(User, user_id=user_id)
    cart_items = ItemsInCart.objects.filter(user=user)
    total_price = sum(item.item.price * item.amount for item in cart_items)
    context = {'cart_items': cart_items, 'total_price': total_price}
    return render(request, 'store/cart.html', context)

def add_to_cart(request, item_id):
    if request.method == 'POST':
        user_id = request.session.get('login_user_id')
        if not user_id: return redirect('accounts:login')
        amount = int(request.POST.get('amount', 1))
        item = get_object_or_404(Item, item_id=item_id)
        user = get_object_or_404(User, user_id=user_id)
        cart_item, created = ItemsInCart.objects.get_or_create(
            user=user, item=item, defaults={'amount': amount}
        )
        if not created:
            cart_item.amount += amount
            cart_item.save()
        return redirect('store:cart')

def update_cart(request, item_id):
    user_id = request.session.get('login_user_id')
    if not user_id: return redirect('accounts:login')
    if request.method == 'POST':
        amount = int(request.POST.get('amount', 1))
        user = get_object_or_404(User, user_id=user_id)
        item = get_object_or_404(Item, item_id=item_id)
        cart_item = get_object_or_404(ItemsInCart, user=user, item=item)
        if amount > 0 and amount <= item.stock:
            cart_item.amount = amount
            cart_item.save()
    return redirect('store:cart')

def delete_cart(request, item_id):
    user_id = request.session.get('login_user_id')
    if not user_id: return redirect('accounts:login')
    user = get_object_or_404(User, user_id=user_id)
    item = get_object_or_404(Item, item_id=item_id)
    ItemsInCart.objects.filter(user=user, item=item).delete()
    return redirect('store:cart')

def checkout(request):
    user_id = request.session.get('login_user_id')
    if not user_id: return redirect('accounts:login')
    user = get_object_or_404(User, user_id=user_id)
    cart_items = ItemsInCart.objects.filter(user=user)
    if not cart_items: return redirect('store:cart')

    total_price = sum(item.item.price * item.amount for item in cart_items)
    coupons = Coupon.objects.filter(user=user)

    context = {
        'user': user,
        'cart_items': cart_items,
        'total_price': total_price,
        'coupons': coupons,
    }
    return render(request, 'store/checkout.html', context)

def checkoutCommit(request):
    user_id = request.session.get('login_user_id')
    if not user_id: return redirect('accounts:login')
    if request.method != 'POST': return redirect('store:cart')

    destination = request.POST.get('destination')
    card_number = request.POST.get('card_number', '4242424242424242')
    coupon_id = request.POST.get('coupon_id')  # 適用するクーポンID
    user = get_object_or_404(User, user_id=user_id)
    cart_items = ItemsInCart.objects.filter(user=user)
    if not cart_items: return redirect('store:cart')

    original_total = sum(c.item.price * c.amount for c in cart_items)
    total_price = original_total

    # クーポンを適用
    coupon = None
    if coupon_id:
        coupon = get_object_or_404(Coupon, id=coupon_id, user=user)
        if coupon.coupon_type == '20%':
            total_price = int(total_price * 0.8)
        elif coupon.coupon_type == '50%':
            total_price = int(total_price * 0.5)
        elif coupon.coupon_type == '99%':
            total_price = int(total_price * 0.01)

    # 決済APIにリクエスト
    api_base_url = os.environ.get('API_BASE_URL', 'http://15.152.44.182/api/v1')
    api_key = os.environ.get('API_KEY', '')
    payment_success = False
    payment_data = {}

    try:
        res = requests.post(
            f"{api_base_url}/payments/charge",
            headers={
                'X-API-Key': api_key,
                'Content-Type': 'application/json',
            },
            json={
                'amount': total_price,
                'currency': 'JPY',
                'card_number': card_number,
                'description': f'User:{user_id}',
            },
            timeout=10,
        )
        if res.status_code in [200, 201]:
            payment_data = res.json()
            if payment_data.get('status') == 'succeeded':
                payment_success = True
    except requests.exceptions.RequestException:
        pass

    if not payment_success:
        error_message = '決済に失敗しました。カード情報を確認して再度お試しください。'
        if payment_data.get('error'):
            error_message += f"（{payment_data['error'].get('message', '')}）"
        coupons = Coupon.objects.filter(user=user)
        context = {
            'user': user,
            'cart_items': cart_items,
            'total_price': original_total,
            'coupons': coupons,
            'error_message': error_message,
        }
        return render(request, 'store/checkout.html', context)

    # 決済成功時：注文をDBに保存
    with transaction.atomic():
        for c_item in cart_items:
            if c_item.amount > c_item.item.stock:
                return redirect('store:cart')
        max_p = Purchase.objects.aggregate(Max('purchase_id'))['purchase_id__max']
        next_p_id = (max_p or 0) + 1

        # クーポン適用があれば割引後金額を、なければ None を保存
        discounted_total = total_price if coupon_id else None

        purchase = Purchase.objects.create(
            purchase_id=next_p_id,
            destination=destination,
            user=user,
            transaction_id=payment_data.get('transaction_id', ''),
            payment_status=payment_data.get('status', 'unknown'),
            card_last4=payment_data.get('card_last4', ''),
            discounted_total=discounted_total,
        )
        max_pd = PurchaseDetail.objects.aggregate(Max('purchase_detail_id'))['purchase_detail_id__max']
        next_pd_id = (max_pd or 0) + 1
        for c_item in cart_items:
            PurchaseDetail.objects.create(purchase_detail_id=next_pd_id, amount=c_item.amount, item=c_item.item, purchase=purchase)
            next_pd_id += 1
            c_item.item.stock -= c_item.amount
            c_item.item.save()
        cart_items.delete()

        # 適用したクーポンを削除
        if coupon:
            coupon.delete()

    return render(request, 'store/purchaseComplete.html', {'purchase': purchase})


# 管理者メインページ（商品検索一覧）
def adminMain(request):
    admin_id = request.session.get('admin_login_id')
    if not admin_id: return redirect('accounts:adminLogin')

    # 管理者用商品検索処理
    keyword = request.GET.get('keyword')
    category_id = request.GET.get('category')
    
    items = Item.objects.all()
    if keyword:
        items = items.filter(name__icontains=keyword)
    if category_id:
        items = items.filter(category_id=category_id)

    categories = Category.objects.all()
    
    context = {
        'items': items,
        'categories': categories,
        'admin_id': admin_id,
        'keyword': keyword,
        'category_id': category_id,
    }
    return render(request, 'store/adminMain.html', context)

# 商品の新規登録
def adminItemAdd(request):
    admin_id = request.session.get('admin_login_id')
    if not admin_id: return redirect('accounts:adminLogin')
    
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('store:adminMain')
    else:
        form = ItemForm()
        
    return render(request, 'store/adminItemForm.html', {'form': form, 'title': '商品新規登録'})

# 商品の修正
def adminItemEdit(request, item_id):
    admin_id = request.session.get('admin_login_id')
    if not admin_id: return redirect('accounts:adminLogin')
    
    item = get_object_or_404(Item, item_id=item_id)
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('store:adminMain')
    else:
        form = ItemForm(instance=item)
        # 主キー(ID)は修正不可にする設定
        form.fields['item_id'].widget.attrs['readonly'] = True
        
    return render(request, 'store/adminItemForm.html', {'form': form, 'title': '商品情報修正'})

# 商品の削除
def adminItemDelete(request, item_id):
    admin_id = request.session.get('admin_login_id')
    if not admin_id: return redirect('accounts:adminLogin')
    
    if request.method == 'POST':
        item = get_object_or_404(Item, item_id=item_id)
        item.delete()
    return redirect('store:adminMain')

# 商品のおすすめ指定切り替え
def adminItemToggleRecommend(request, item_id):
    admin_id = request.session.get('admin_login_id')
    if not admin_id: return redirect('accounts:adminLogin')
    
    item = get_object_or_404(Item, item_id=item_id)
    item.recommended = not item.recommended
    item.save()
    return redirect('store:adminMain')

# 管理者用 注文履歴検索・一覧画面
def adminPurchaseList(request):
    admin_id = request.session.get('admin_login_id')
    if not admin_id: return redirect('accounts:adminLogin')

    # 検索キーワード（注文ID または 会員ID を想定）
    keyword = request.GET.get('keyword')
    
    # 最新の注文から順に取得
    purchases = Purchase.objects.all().order_by('-booked_date')

    if keyword:
        # 注文IDと完全一致、または会員IDにキーワードが含まれるものを検索
        purchases = purchases.filter(purchase_id__icontains=keyword) | purchases.filter(user__user_id__icontains=keyword)

    # テンプレートで扱いやすいように、注文ごとに詳細と合計金額をまとめる
    purchase_data = []
    for p in purchases:
        details = PurchaseDetail.objects.filter(purchase=p)
        subtotal = sum(d.item.price * d.amount for d in details)
        # discounted_total が保存されていればそちらを、なければ小計をそのまま使う
        total_price = p.discounted_total if p.discounted_total is not None else subtotal
        purchase_data.append({
            'purchase': p,
            'details': details,
            'total_price': total_price
        })

    return render(request, 'store/adminPurchaseList.html', {'purchase_data': purchase_data, 'keyword': keyword})

# 管理者用 注文キャンセル処理
def adminPurchaseCancel(request, purchase_id):
    admin_id = request.session.get('admin_login_id')
    if not admin_id: return redirect('accounts:adminLogin')

    if request.method == 'POST':
        purchase = get_object_or_404(Purchase, purchase_id=purchase_id)
        
        # まだキャンセルされていない場合のみ処理を実行
        if not purchase.cancel:
            # トランザクションで安全に処理（途中でエラーが起きたら元に戻す）
            with transaction.atomic():
                # 注文のキャンセルステータスをTrueに変更
                purchase.cancel = True
                purchase.save()
                
                # キャンセルされた注文に含まれる商品の「在庫を元に戻す」処理
                details = PurchaseDetail.objects.filter(purchase=purchase)
                for detail in details:
                    detail.item.stock += detail.amount
                    detail.item.save()

    return redirect('store:adminPurchaseList')


from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import Coupon, User  # 独自のUserモデルをインポート
import random

def coupon_view(request):
    user_id = request.session.get('login_user_id')
    if not user_id: 
        return redirect('accounts:login')

    user = get_object_or_404(User, user_id=user_id)

    existing_coupons = Coupon.objects.filter(user=user)

    if existing_coupons.count() >= 3:
        return render(request, 'store/coupon.html', {'message': 'You already have 3 coupons!', 'already_max': True})

    coupon_type = random.choice(['20%', '50%', '99%'])
    Coupon.objects.create(user=user, coupon_type=coupon_type)

    return render(request, 'store/coupon.html', {'coupon_type': coupon_type})

# チャットボット
def itemChat(request, item_id):
    if request.method != 'POST':
        return redirect('store:itemDetail', item_id=item_id)

    item = get_object_or_404(Item, item_id=item_id)
    user_message = request.POST.get('message', '').strip()

    if not user_message:
        return redirect('store:itemDetail', item_id=item_id)

    # Gemini APIの設定
    api_key = os.environ.get('GEMINI_API_KEY', '')
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.5-flash')

    # 商品情報をシステムプロンプトに含める
    system_prompt = f"""
あなたは「{item.name}」という商品を販売するECサイトのサポートスタッフです。
以下の商品情報をもとに、お客様の質問に日本語で丁寧に答えてください。

【商品情報】
- 商品名: {item.name}
- メーカー: {item.manufacturer}
- 色: {item.color}
- 価格: {item.price}円
- 在庫数: {item.stock}個
- カテゴリ: {item.category.name}

商品情報に含まれていない質問には「詳細はお問い合わせください」と答えてください。
回答は2〜3文程度で簡潔にまとめてください。
"""

    try:
        response = model.generate_content(f"{system_prompt}\n\nお客様の質問: {user_message}")
        bot_reply = response.text
    except Exception:
        bot_reply = '申し訳ありません。現在チャットボットが利用できません。'

    # セッションにチャット履歴を保存
    chat_history = request.session.get('chat_history', {})
    if str(item_id) not in chat_history:
        chat_history[str(item_id)] = []
    chat_history[str(item_id)].append({
        'user': user_message,
        'bot': bot_reply,
    })
    request.session['chat_history'] = chat_history

    return redirect('store:itemDetail', item_id=item_id)


def add_review(request, item_id):
    login_user_id = request.session.get("login_user_id")

    if not login_user_id:
        return redirect("accounts:login")

    item = get_object_or_404(Item, item_id=item_id)
    user = get_object_or_404(User, user_id=login_user_id)

    if request.method == "POST":
        form = ReviewForm(request.POST)

        if form.is_valid():
            has_purchase = PurchaseDetail.objects.filter(
                item=item,
                purchase__user=user,
                purchase__cancel=False
            ).exists()

            Review.objects.update_or_create(
                item=item,
                user=user,
                defaults={
                    "rating": int(form.cleaned_data["rating"]),
                    "title": form.cleaned_data["title"],
                    "comment": form.cleaned_data["comment"],
                    "is_verified_purchase": has_purchase,
                }
            )

    return redirect("store:itemDetail", item_id=item.item_id)

import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST

# メインページ サポートチャットボット
@require_POST
def supportChat(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
    except Exception:
        return JsonResponse({'reply': 'メッセージの形式が不正です。'}, status=400)

    if not user_message:
        return JsonResponse({'reply': 'メッセージを入力してください。'})

    # 商品情報を取得してプロンプトに含める
    items = Item.objects.select_related('category').all()
    categories = Category.objects.all()

    item_list = '\n'.join([
        f"- [{item.category.name}] {item.name}（{item.color}）¥{item.price} 在庫{item.stock}個"
        + ('【おすすめ】' if item.recommended else '')
        for item in items
    ])
    category_list = '・'.join([cat.name for cat in categories])

    system_prompt = f"""
あなたはECサイト「SOUGOU STORE」のサポートスタッフです。
お客様の要望を聞いて、以下の商品リストからぴったりの商品を提案してください。

【取り扱いカテゴリ】
{category_list}

【商品一覧】
{item_list}

【回答ルール】
- 最初に一言だけ簡潔に答えてください（1文以内）
- おすすめ商品は以下の形式で箇条書きにしてください（最大3件）：
  • 商品名 / ¥価格 / カテゴリ
- 商品リストにない質問（配送・返品など）には「詳細はお問い合わせください」とだけ答えてください
- 余計な説明や締めの言葉は不要です
- 日本語で答えてください
"""

    api_key = os.environ.get('GEMINI_API_KEY', '')
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.5-flash')

    try:
        response = model.generate_content(f"{system_prompt}\n\nお客様: {user_message}")
        reply = response.text
    except Exception:
        reply = '申し訳ありません。現在チャットボットが利用できません。'

    # try:
    #     response = model.generate_content(f"{system_prompt}\n\nお客様: {user_message}")
    #     reply = response.text
    #     print(repr(reply))  # 改行文字を確認
    # except Exception:
    #     reply = '申し訳ありません。現在チャットボットが利用できません。'

    return JsonResponse({'reply': reply})