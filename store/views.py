from django.shortcuts import render, get_object_or_404
from .models import Item, Category  # Categoryを追加

# 商品検索・一覧画面 (S01)
def main(request):
    items = Item.objects.all()
    categories = Category.objects.all()  # 全カテゴリを取得
    
    context = {
        'items': items,
        'categories': categories,  # テンプレートに渡す
    }
    return render(request, 'store/main.html', context)

# 商品詳細画面 (S03)
def itemDetail(request, item_id):
    item = get_object_or_404(Item, item_id=item_id)
    context = {
        'item': item
    }
    return render(request, 'store/itemDetail.html', context)

# 検索結果画面 (S02)
def searchResult(request):
    # GETリクエストから検索条件を取得
    keyword = request.GET.get('keyword')
    category_id = request.GET.get('category')

    # まず全ての商品を取得
    results = Item.objects.all()

    # キーワードが入力されていれば、商品名にその文字が含まれるものを絞り込み (icontains)
    if keyword:
        results = results.filter(name__icontains=keyword)

    # カテゴリが選択されていれば、そのカテゴリIDで絞り込み
    if category_id:
        results = results.filter(category_id=category_id)

    context = {
        'results': results,
        'keyword': keyword,
    }
    return render(request, 'store/searchResult.html', context)

# ショッピングカート画面 (S04)
def cart(request):
    return render(request, 'store/cart.html')