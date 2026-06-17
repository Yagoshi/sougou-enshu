"""
カラフルな商品20件を追加するスクリプト

使い方:
    python generate_colorful_items.py
"""

import os
import sys
import time
import django
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop01.settings')
django.setup()

from google import genai
from google.genai import types
from django.core.files.base import ContentFile
from django.db.models import Max
from store.models import Category, Item

client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))

COLORFUL_ITEMS = [
    # (name, manufacturer, color, price, stock, recommended, category_id, image_prompt)
    # 鞄
    ("ポップカラートートバッグ",     "VIVID工房",   "イエロー",          3800, 30, False, 1, "Bright yellow tote bag, vivid colorful, product photo, white background, bold color"),
    ("レインボーバックパック",        "COLOR社",     "レインボー",        5200, 20, True,  1, "Rainbow colorful backpack, multicolor gradient, product photo, white background"),
    ("コーラルピンクポーチ",         "PASTEL工房",  "コーラルピンク",    2200, 40, False, 1, "Coral pink pouch bag, vibrant color, product photo, white background"),
    ("エレクトリックブルークラッチ",  "NEON社",      "エレクトリックブルー", 3500, 25, False, 1, "Electric blue clutch bag, vivid bold color, product photo, white background"),

    # 帽子
    ("ホットピンクベレー帽",         "VIVID帽子社", "ホットピンク",      2800, 35, False, 2, "Hot pink beret hat, vibrant color, product photo, white background"),
    ("イエローグリーンキャップ",     "NEON工房",    "イエローグリーン",  3200, 28, True,  2, "Yellow green neon cap, vivid color, product photo, white background"),
    ("オレンジバケットハット",       "COLOR帽子社", "オレンジ",          2500, 40, False, 2, "Bright orange bucket hat, bold color, product photo, white background"),

    # 衣類
    ("ラベンダースウェット",         "PASTEL工房",  "ラベンダー",        4500, 30, False, 3, "Lavender pastel sweatshirt, soft color, product photo, white background"),
    ("マゼンタTシャツ",             "BOLD社",      "マゼンタ",          2200, 50, False, 3, "Magenta bold t-shirt, vibrant color, product photo, white background"),
    ("コバルトブルーニットセーター", "VIVID工房",   "コバルトブルー",    7800, 18, True,  3, "Cobalt blue knit sweater, vivid bold color, product photo, white background"),
    ("ライムグリーンジャケット",     "COLOR社",     "ライムグリーン",    8500, 15, True,  3, "Lime green jacket, vivid color, product photo, white background"),
    ("サンセットオレンジワンピース", "SUNSET工房",  "オレンジ×ピンク",  6800, 20, False, 3, "Orange pink sunset gradient dress, colorful, product photo, white background"),
    ("タイダイパターンTシャツ",     "TIE工房",     "マルチカラー",      3200, 35, False, 3, "Tie-dye multicolor t-shirt, colorful pattern, product photo, white background"),
    ("ターコイズブルーカーディガン", "VIVID社",     "ターコイズ",        6200, 22, False, 3, "Turquoise blue cardigan, vivid color, product photo, white background"),

    # シューズ
    ("ネオングリーンスニーカー",     "NEON靴社",    "ネオングリーン",    7200, 20, True,  4, "Neon green sneakers, vivid bold color, product photo, white background"),
    ("コーラルサンダル",            "COLOR靴工房", "コーラル",          5500, 25, False, 4, "Coral orange sandals, vibrant color, product photo, white background"),
    ("パープルハイカットスニーカー", "VIVID靴社",   "パープル",          8800, 15, True,  4, "Purple high-top sneakers, bold color, product photo, white background"),

    # アクセサリー
    ("カラフルビーズブレスレット",  "BEAD工房",    "マルチカラー",      1800, 60, False, 5, "Multicolor beads bracelet, colorful, product photo, white background, jewelry"),
    ("エメラルドグリーンピアス",    "GEM社",       "エメラルドグリーン", 4800, 25, True,  5, "Emerald green earrings, vivid color, product photo, white background, jewelry"),
    ("サンセットイヤリング",        "SUNSET工房",  "オレンジ×イエロー", 3500, 30, False, 5, "Orange yellow sunset gradient earrings, colorful, product photo, white background, jewelry"),
]


def generate_image(prompt: str) -> bytes | None:
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash-image',
            contents=f"Product photography: {prompt}, clean white background, studio lighting, high quality",
            config=types.GenerateContentConfig(response_modalities=['IMAGE'])
        )
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                return part.inline_data.data
    except Exception as e:
        print(f"  ⚠️  画像生成エラー: {e}")
    return None


def main():
    print("=" * 60)
    print("カラフル商品 追加スクリプト")
    print(f"追加件数: {len(COLORFUL_ITEMS)}件")
    print("=" * 60)

    max_id = Item.objects.aggregate(Max('item_id'))['item_id__max'] or 0
    start_id = max_id + 1
    print(f"開始ID: {start_id}")

    success_count = 0
    error_count = 0

    for i, (name, manufacturer, color, price, stock, recommended, cat_id, prompt) in enumerate(COLORFUL_ITEMS):
        item_id = start_id + i
        print(f"\n[{i+1:2d}/{len(COLORFUL_ITEMS)}] {name} ({color})")

        try:
            category = Category.objects.get(category_id=cat_id)
        except Category.DoesNotExist:
            print(f"  ❌ カテゴリID {cat_id} が存在しません。スキップ")
            error_count += 1
            continue

        if Item.objects.filter(name=name).exists():
            print(f"  ⏭️  既に存在するのでスキップ")
            continue

        print(f"  🎨 画像生成中...")
        image_data = generate_image(prompt)

        item = Item(
            item_id=item_id,
            name=name,
            manufacturer=manufacturer,
            color=color,
            price=price,
            stock=stock,
            recommended=recommended,
            category=category,
        )

        if image_data:
            filename = f"item_{item_id}_{name[:8].replace(' ', '_')}.png"
            item.image.save(filename, ContentFile(image_data), save=False)
            print(f"  ✅ 画像保存完了")
        else:
            print(f"  ⚠️  画像なしで登録")

        item.save()
        success_count += 1
        print(f"  💾 DB保存完了 (item_id={item_id})")

        if i < len(COLORFUL_ITEMS) - 1:
            print(f"  ⏳ 7秒待機中...")
            time.sleep(7)

    print("\n" + "=" * 60)
    print(f"✅ 完了！ 成功: {success_count}件 / エラー: {error_count}件")
    print("=" * 60)


if __name__ == '__main__':
    main()
