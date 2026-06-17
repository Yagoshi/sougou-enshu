"""
Gemini APIで商品画像を生成しながら100件のデータを投入するスクリプト

使い方:
    python generate_items.py

注意:
    - プロジェクトルート（manage.pyと同じ場所）で実行してください
    - .envファイルにGEMINI_API_KEYが設定されている必要があります
    - 無料枠: 1日500枚まで（2分に1枚のペースで実行）
"""

import os
import sys
import time
import django
from pathlib import Path
from dotenv import load_dotenv

# Django設定の初期化
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop01.settings')
django.setup()

from google import genai
from google.genai import types
from django.core.files.base import ContentFile
from store.models import Category, Item

# ── Geminiクライアント初期化 ──
client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))

# ── 投入する商品データ定義 ──
ITEMS_DATA = [
    # (name, manufacturer, color, price, stock, recommended, category_id, image_prompt)
    # 鞄 (category_id=1)
    ("レザートートバッグ Mサイズ",        "CRAFT工房",     "キャメル",   8800,  20, True,  1, "Brown leather tote bag, product photo, white background, minimal"),
    ("ナイロンリュック 30L",              "TRAIL社",       "ブラック",   5980,  35, False, 1, "Black nylon backpack 30L, product photo, white background"),
    ("キャンバスショルダーバッグ",          "DAILY製作所",   "ネイビー",   3480,  50, False, 1, "Navy canvas shoulder bag, product photo, white background"),
    ("PUレザークラッチバッグ",             "URBAN工房",     "ブラウン",   4200,  25, False, 1, "Brown PU leather clutch bag, product photo, white background"),
    ("ミニボディバッグ",                   "ACTIVE社",      "グレー",     2980,  40, False, 1, "Gray mini body bag, product photo, white background"),
    ("ビジネスリュック 撥水加工",          "OFFICE製作所",  "ブラック",   9800,  18, True,  1, "Black business backpack waterproof, product photo, white background"),
    ("ウィークエンドボストンバッグ",        "TRAVEL工房",    "ベージュ",   7500,  15, False, 1, "Beige weekend Boston bag, product photo, white background"),
    ("メッシュトートバッグ 夏用",          "BEACH社",       "ホワイト",   1980,  60, False, 1, "White mesh tote bag summer, product photo, white background"),
    ("コルクハンドバッグ エコ素材",        "ECO工房",       "ナチュラル", 6800,  12, True,  1, "Natural cork handbag eco material, product photo, white background"),
    ("レザーウォレットバッグ",             "SLIM製作所",    "ブラック",   5500,  22, False, 1, "Black leather wallet bag, product photo, white background"),
    ("帆布トートバッグ 大容量",            "CANVAS工房",    "オリーブ",   3200,  45, False, 1, "Olive canvas tote bag large, product photo, white background"),
    ("レザーダッフルバッグ",               "JOURNEY社",     "タン",       12800, 10, True,  1, "Tan leather duffle bag, product photo, white background"),
    ("折りたたみエコバッグ",               "FOLD製作所",    "グリーン",   980,   80, False, 1, "Green foldable eco bag, product photo, white background"),
    ("スエードポーチバッグ",               "SUEDE工房",     "ピンク",     2800,  30, False, 1, "Pink suede pouch bag, product photo, white background"),
    ("ミリタリーバックパック",             "ARMY社",        "カーキ",     6200,  20, False, 1, "Khaki military backpack, product photo, white background"),
    ("透明ビニールバッグ",                 "CLEAR製作所",   "クリア",     2200,  35, False, 1, "Clear vinyl transparent bag, product photo, white background"),
    ("ウーブンバスケットバッグ",           "BASKET工房",    "ベージュ",   4500,  18, True,  1, "Beige woven basket bag, product photo, white background"),
    ("スポーツジムバッグ",                 "FITNESS社",     "ブルー",     4800,  28, False, 1, "Blue sports gym bag, product photo, white background"),
    ("ビーチトートバッグ XL",             "SUMMER製作所",  "ストライプ", 3600,  40, False, 1, "Striped beach tote bag XL, product photo, white background"),
    ("レザーブリーフケース",               "BUSINESS工房",  "ダークブラウン", 15800, 8, True, 1, "Dark brown leather briefcase, product photo, white background"),

    # 帽子 (category_id=2)
    ("ウールベレー帽",                     "HAT工房",       "グレー",     3200,  30, True,  2, "Gray wool beret hat, product photo, white background"),
    ("ストローハット ナチュラル",          "SUMMER帽子社",  "ナチュラル", 4500,  25, False, 2, "Natural straw hat, product photo, white background"),
    ("ニットキャップ ポンポン付き",        "WINTER工房",    "レッド",     2200,  50, False, 2, "Red knit cap with pompom, product photo, white background"),
    ("バケットハット デニム",              "CASUAL帽子社",  "インディゴ", 2800,  40, True,  2, "Indigo denim bucket hat, product photo, white background"),
    ("キャップ ロゴ刺繍 5パネル",         "SPORT工房",     "ホワイト",   3500,  35, False, 2, "White 5-panel cap logo embroidery, product photo, white background"),
    ("パナマハット 折りたたみ可能",        "TRAVEL帽子社",  "ベージュ",   6800,  15, True,  2, "Beige Panama hat foldable, product photo, white background"),
    ("フェドーラハット ウール混",          "CLASSIC工房",   "ブラック",   5500,  20, False, 2, "Black wool fedora hat, product photo, white background"),
    ("ビーニー リブ編み",                  "KNIT帽子社",    "ネイビー",   1800,  60, False, 2, "Navy ribbed knit beanie, product photo, white background"),
    ("サファリハット UVカット",            "OUTDOOR工房",   "カーキ",     3800,  28, False, 2, "Khaki safari hat UV protection, product photo, white background"),
    ("ハット つば広 リボン付き",           "ELEGANT帽子社", "ブラック",   4200,  22, True,  2, "Black wide brim hat with ribbon, product photo, white background"),

    # 衣類 (category_id=3)
    ("オーバーサイズスウェット",           "COMFY社",       "グレー",     4800,  40, True,  3, "Gray oversized sweatshirt, product photo, white background"),
    ("リネンシャツ 半袖",                  "LINEN工房",     "ホワイト",   5800,  30, False, 3, "White linen short sleeve shirt, product photo, white background"),
    ("ストレッチチノパンツ",               "TAILOR社",      "ベージュ",   6500,  25, False, 3, "Beige stretch chino pants, product photo, white background"),
    ("ニットカーディガン Vネック",         "KNIT工房",      "キャメル",   7200,  20, True,  3, "Camel V-neck knit cardigan, product photo, white background"),
    ("テーパードデニムジーンズ",           "DENIM社",       "インディゴ", 8900,  22, False, 3, "Indigo tapered denim jeans, product photo, white background"),
    ("フリースジャケット ジップアップ",   "OUTDOOR工房",   "グリーン",   6800,  18, False, 3, "Green fleece jacket zip-up, product photo, white background"),
    ("プリントTシャツ グラフィック",      "GRAPHIC社",     "ブラック",   2800,  55, False, 3, "Black graphic print t-shirt, product photo, white background"),
    ("ワイドレッグパンツ ハイウエスト",   "FASHION工房",   "ブラック",   7500,  20, True,  3, "Black high waist wide leg pants, product photo, white background"),
    ("ボーダーロングスリーブシャツ",      "MARINE社",      "ホワイト×ネイビー", 3800, 35, False, 3, "White navy striped long sleeve shirt, product photo, white background"),
    ("モックネックセーター",               "WOOL工房",      "ブラウン",   8500,  15, True,  3, "Brown mock neck sweater, product photo, white background"),
    ("コットンワンピース フレア",          "CASUAL社",      "フラワー",   6200,  25, False, 3, "Floral cotton flare dress, product photo, white background"),
    ("ウインドブレーカー 撥水",           "SPORT工房",     "オレンジ",   5500,  20, False, 3, "Orange windbreaker waterproof, product photo, white background"),
    ("ショートパンツ スウェット素材",     "COMFY社",       "グレー",     3200,  40, False, 3, "Gray sweat shorts, product photo, white background"),
    ("クロップドジャケット ツイード",     "ELEGANT工房",   "チェック",   12800, 10, True,  3, "Tweed check cropped jacket, product photo, white background"),
    ("ロングカーディガン ニット",         "KNIT社",        "アイボリー", 9800,  12, False, 3, "Ivory long knit cardigan, product photo, white background"),
    ("スキニーパンツ ハイストレッチ",     "FIT工房",       "ブラック",   5800,  30, False, 3, "Black high stretch skinny pants, product photo, white background"),
    ("オーバーオール デニム",             "DENIM社",       "ライトブルー", 8200, 18, False, 3, "Light blue denim overalls, product photo, white background"),
    ("ポロシャツ 半袖",                   "POLO工房",      "ホワイト",   4500,  35, True,  3, "White polo shirt short sleeve, product photo, white background"),
    ("チェスターコート ウール混",         "WINTER社",      "グレー",     18800, 8,  True,  3, "Gray wool chester coat, product photo, white background"),
    ("ハーフジップスウェット",            "ACTIVE工房",    "ネイビー",   5200,  28, False, 3, "Navy half zip sweatshirt, product photo, white background"),

    # シューズ (category_id=4)
    ("レザーローファー スリッポン",       "SHOES工房",     "ブラック",   12800, 15, True,  4, "Black leather loafer slip-on, product photo, white background"),
    ("スニーカー キャンバス",             "CASUAL靴社",    "ホワイト",   6800,  30, False, 4, "White canvas sneakers, product photo, white background"),
    ("サンダル レザーソール",             "SUMMER工房",    "タン",       8500,  20, False, 4, "Tan leather sole sandals, product photo, white background"),
    ("チェルシーブーツ スエード",         "BOOT社",        "チャコール", 15800, 12, True,  4, "Charcoal suede Chelsea boots, product photo, white background"),
    ("スリッポン エスパドリーユ",         "SPAIN工房",     "ネイビー",   5200,  25, False, 4, "Navy espadrille slip-on, product photo, white background"),
    ("ハイカットスニーカー",              "SPORT靴社",     "ブラック",   9800,  18, True,  4, "Black high-top sneakers, product photo, white background"),
    ("パンプス ポインテッドトゥ",         "HEEL工房",      "ヌード",     11800, 15, False, 4, "Nude pointed toe pumps, product photo, white background"),
    ("デッキシューズ",                    "MARINE靴社",    "ネイビー",   7800,  22, False, 4, "Navy deck shoes, product photo, white background"),
    ("ランニングシューズ クッション",     "RUN工房",       "ライムグリーン", 9200, 20, True, 4, "Lime green cushion running shoes, product photo, white background"),
    ("ウォーキングシューズ 幅広",         "WALK靴社",      "グレー",     8500,  18, False, 4, "Gray wide walking shoes, product photo, white background"),
    ("モカシン スエード",                 "MOCA工房",      "キャメル",   7200,  20, False, 4, "Camel suede moccasins, product photo, white background"),
    ("ミュール ヒール付き",               "MULE靴社",      "ホワイト",   8800,  15, False, 4, "White heeled mules, product photo, white background"),
    ("トレッキングシューズ",              "MOUNTAIN工房",  "オリーブ",   14800, 12, True,  4, "Olive trekking shoes, product photo, white background"),
    ("バレエシューズ フラット",           "DANCE靴社",     "ブラック",   5500,  30, False, 4, "Black flat ballet shoes, product photo, white background"),
    ("アンクルブーツ レザー",            "BOOT工房",      "ブラウン",   13800, 10, True,  4, "Brown leather ankle boots, product photo, white background"),

    # アクセサリー (category_id=5)
    ("シルバーリング シンプル",           "SILVER工房",    "シルバー",   3200,  40, False, 5, "Silver simple ring, product photo, white background, jewelry"),
    ("パールネックレス 淡水",             "PEARL社",       "ホワイト",   8800,  20, True,  5, "White freshwater pearl necklace, product photo, white background, jewelry"),
    ("レザーブレスレット",                "LEATHER工房",   "ブラウン",   2800,  35, False, 5, "Brown leather bracelet, product photo, white background, jewelry"),
    ("ゴールドフープイヤリング",          "GOLD社",        "ゴールド",   4500,  30, True,  5, "Gold hoop earrings, product photo, white background, jewelry"),
    ("シルクスカーフ 正方形",             "SILK工房",      "マルチカラー", 6800, 20, False, 5, "Multicolor silk square scarf, product photo, white background"),
    ("アンティーク調ブローチ",            "BROOCH社",      "ゴールド",   3800,  25, False, 5, "Gold antique style brooch, product photo, white background, jewelry"),
    ("皮革手袋 スマホ対応",              "GLOVE工房",     "ブラック",   5500,  18, True,  5, "Black leather gloves smartphone compatible, product photo, white background"),
    ("ウールマフラー チェック",           "SCARF社",       "レッド×グレー", 4200, 30, False, 5, "Red gray check wool muffler, product photo, white background"),
    ("サングラス スクエア型",             "SUN工房",       "ブラック",   7800,  22, True,  5, "Black square sunglasses, product photo, white background"),
    ("ヘアバンド リボン付き",             "HAIR社",        "ブラック",   1800,  50, False, 5, "Black hair band with ribbon, product photo, white background"),
    ("チタンリング",                      "TITAN工房",     "シルバー",   5800,  20, False, 5, "Silver titanium ring, product photo, white background, jewelry"),
    ("天然石ブレスレット",               "STONE社",       "パープル",   4200,  28, True,  5, "Purple natural stone bracelet, product photo, white background, jewelry"),
    ("レザーベルト ゴールドバックル",    "BELT工房",      "ブラウン",   5200,  25, False, 5, "Brown leather belt gold buckle, product photo, white background"),
    ("ニットヘアバンド",                  "KNIT社",        "ベージュ",   1500,  60, False, 5, "Beige knit hair band, product photo, white background"),
    ("アクリルバングル セット",           "BANGLE工房",    "クリア",     2800,  35, False, 5, "Clear acrylic bangle set, product photo, white background, jewelry"),
]


def generate_image(prompt: str) -> bytes | None:
    """Gemini APIで画像を生成してbytesで返す"""
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash-image',
            contents=f"Product photography: {prompt}, clean white background, studio lighting, high quality",
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE']
            )
        )
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                return part.inline_data.data
    except Exception as e:
        print(f"  ⚠️  画像生成エラー: {e}")
    return None


def main():
    print("=" * 60)
    print("商品データ＋画像生成 一括投入スクリプト")
    print(f"投入件数: {len(ITEMS_DATA)}件")
    print("=" * 60)

    # 既存の最大item_idを取得（seedデータと被らないように200番台から開始）
    from django.db.models import Max
    max_id = Item.objects.aggregate(Max('item_id'))['item_id__max'] or 0
    start_id = max(max_id + 1, 200)

    success_count = 0
    error_count = 0

    for i, (name, manufacturer, color, price, stock, recommended, cat_id, prompt) in enumerate(ITEMS_DATA):
        item_id = start_id + i
        print(f"\n[{i+1:3d}/{len(ITEMS_DATA)}] {name}")

        try:
            category = Category.objects.get(category_id=cat_id)
        except Category.DoesNotExist:
            print(f"  ❌ カテゴリID {cat_id} が存在しません。スキップします。")
            error_count += 1
            continue

        # 既に存在する場合はスキップ
        if Item.objects.filter(name=name).exists():
            print(f"  ⏭️  既に存在するのでスキップ")
            continue

        # 画像生成
        print(f"  🎨 画像生成中...")
        image_data = generate_image(prompt)

        # 商品をDBに保存
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
            filename = f"item_{item_id}_{name[:10].replace(' ', '_')}.png"
            item.image.save(filename, ContentFile(image_data), save=False)
            print(f"  ✅ 画像保存: {filename}")
        else:
            print(f"  ⚠️  画像なしで登録")

        item.save()
        success_count += 1
        print(f"  💾 DB保存完了 (item_id={item_id})")

        # レート制限対策（無料枠: 10 RPM）
        if i < len(ITEMS_DATA) - 1:
            print(f"  ⏳ 7秒待機中...")
            time.sleep(7)

    print("\n" + "=" * 60)
    print(f"✅ 完了！ 成功: {success_count}件 / エラー: {error_count}件")
    print("=" * 60)


if __name__ == '__main__':
    main()
