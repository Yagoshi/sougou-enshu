"""
カテゴリ登録・既存商品クリア・画像付き商品の一括登録を行うスクリプト
（Gemini API不要・画像生成なし）

使い方:
    python register_items_with_images.py

前提:
    - media/items/ に画像ファイルが存在すること
"""

import os
import sys
import django
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop01.settings')
django.setup()

from store.models import Category, Item

# ══════════════════════════════════════════════
# カテゴリデータ
# ══════════════════════════════════════════════
CATEGORIES_DATA = [
    (1, "鞄"),
    (2, "帽子"),
    (3, "衣類"),
    (4, "シューズ"),
    (5, "アクセサリー"),
]

# ══════════════════════════════════════════════
# generate_items.py の商品データ（80件, ID: 200〜279）
# ══════════════════════════════════════════════
ITEMS_DATA = [
    # (name, manufacturer, color, price, stock, recommended, category_id)
    # 鞄 (category_id=1)
    ("レザートートバッグ Mサイズ",        "CRAFT工房",     "キャメル",   8800,  20, True,  1),
    ("ナイロンリュック 30L",              "TRAIL社",       "ブラック",   5980,  35, False, 1),
    ("キャンバスショルダーバッグ",          "DAILY製作所",   "ネイビー",   3480,  50, False, 1),
    ("PUレザークラッチバッグ",             "URBAN工房",     "ブラウン",   4200,  25, False, 1),
    ("ミニボディバッグ",                   "ACTIVE社",      "グレー",     2980,  40, False, 1),
    ("ビジネスリュック 撥水加工",          "OFFICE製作所",  "ブラック",   9800,  18, True,  1),
    ("ウィークエンドボストンバッグ",        "TRAVEL工房",    "ベージュ",   7500,  15, False, 1),
    ("メッシュトートバッグ 夏用",          "BEACH社",       "ホワイト",   1980,  60, False, 1),
    ("コルクハンドバッグ エコ素材",        "ECO工房",       "ナチュラル", 6800,  12, True,  1),
    ("レザーウォレットバッグ",             "SLIM製作所",    "ブラック",   5500,  22, False, 1),
    ("帆布トートバッグ 大容量",            "CANVAS工房",    "オリーブ",   3200,  45, False, 1),
    ("レザーダッフルバッグ",               "JOURNEY社",     "タン",       12800, 10, True,  1),
    ("折りたたみエコバッグ",               "FOLD製作所",    "グリーン",   980,   80, False, 1),
    ("スエードポーチバッグ",               "SUEDE工房",     "ピンク",     2800,  30, False, 1),
    ("ミリタリーバックパック",             "ARMY社",        "カーキ",     6200,  20, False, 1),
    ("透明ビニールバッグ",                 "CLEAR製作所",   "クリア",     2200,  35, False, 1),
    ("ウーブンバスケットバッグ",           "BASKET工房",    "ベージュ",   4500,  18, True,  1),
    ("スポーツジムバッグ",                 "FITNESS社",     "ブルー",     4800,  28, False, 1),
    ("ビーチトートバッグ XL",             "SUMMER製作所",  "ストライプ", 3600,  40, False, 1),
    ("レザーブリーフケース",               "BUSINESS工房",  "ダークブラウン", 15800, 8, True, 1),

    # 帽子 (category_id=2)
    ("ウールベレー帽",                     "HAT工房",       "グレー",     3200,  30, True,  2),
    ("ストローハット ナチュラル",          "SUMMER帽子社",  "ナチュラル", 4500,  25, False, 2),
    ("ニットキャップ ポンポン付き",        "WINTER工房",    "レッド",     2200,  50, False, 2),
    ("バケットハット デニム",              "CASUAL帽子社",  "インディゴ", 2800,  40, True,  2),
    ("キャップ ロゴ刺繍 5パネル",         "SPORT工房",     "ホワイト",   3500,  35, False, 2),
    ("パナマハット 折りたたみ可能",        "TRAVEL帽子社",  "ベージュ",   6800,  15, True,  2),
    ("フェドーラハット ウール混",          "CLASSIC工房",   "ブラック",   5500,  20, False, 2),
    ("ビーニー リブ編み",                  "KNIT帽子社",    "ネイビー",   1800,  60, False, 2),
    ("サファリハット UVカット",            "OUTDOOR工房",   "カーキ",     3800,  28, False, 2),
    ("ハット つば広 リボン付き",           "ELEGANT帽子社", "ブラック",   4200,  22, True,  2),

    # 衣類 (category_id=3)
    ("オーバーサイズスウェット",           "COMFY社",       "グレー",     4800,  40, True,  3),
    ("リネンシャツ 半袖",                  "LINEN工房",     "ホワイト",   5800,  30, False, 3),
    ("ストレッチチノパンツ",               "TAILOR社",      "ベージュ",   6500,  25, False, 3),
    ("ニットカーディガン Vネック",         "KNIT工房",      "キャメル",   7200,  20, True,  3),
    ("テーパードデニムジーンズ",           "DENIM社",       "インディゴ", 8900,  22, False, 3),
    ("フリースジャケット ジップアップ",   "OUTDOOR工房",   "グリーン",   6800,  18, False, 3),
    ("プリントTシャツ グラフィック",      "GRAPHIC社",     "ブラック",   2800,  55, False, 3),
    ("ワイドレッグパンツ ハイウエスト",   "FASHION工房",   "ブラック",   7500,  20, True,  3),
    ("ボーダーロングスリーブシャツ",      "MARINE社",      "ホワイト×ネイビー", 3800, 35, False, 3),
    ("モックネックセーター",               "WOOL工房",      "ブラウン",   8500,  15, True,  3),
    ("コットンワンピース フレア",          "CASUAL社",      "フラワー",   6200,  25, False, 3),
    ("ウインドブレーカー 撥水",           "SPORT工房",     "オレンジ",   5500,  20, False, 3),
    ("ショートパンツ スウェット素材",     "COMFY社",       "グレー",     3200,  40, False, 3),
    ("クロップドジャケット ツイード",     "ELEGANT工房",   "チェック",   12800, 10, True,  3),
    ("ロングカーディガン ニット",         "KNIT社",        "アイボリー", 9800,  12, False, 3),
    ("スキニーパンツ ハイストレッチ",     "FIT工房",       "ブラック",   5800,  30, False, 3),
    ("オーバーオール デニム",             "DENIM社",       "ライトブルー", 8200, 18, False, 3),
    ("ポロシャツ 半袖",                   "POLO工房",      "ホワイト",   4500,  35, True,  3),
    ("チェスターコート ウール混",         "WINTER社",      "グレー",     18800, 8,  True,  3),
    ("ハーフジップスウェット",            "ACTIVE工房",    "ネイビー",   5200,  28, False, 3),

    # シューズ (category_id=4)
    ("レザーローファー スリッポン",       "SHOES工房",     "ブラック",   12800, 15, True,  4),
    ("スニーカー キャンバス",             "CASUAL靴社",    "ホワイト",   6800,  30, False, 4),
    ("サンダル レザーソール",             "SUMMER工房",    "タン",       8500,  20, False, 4),
    ("チェルシーブーツ スエード",         "BOOT社",        "チャコール", 15800, 12, True,  4),
    ("スリッポン エスパドリーユ",         "SPAIN工房",     "ネイビー",   5200,  25, False, 4),
    ("ハイカットスニーカー",              "SPORT靴社",     "ブラック",   9800,  18, True,  4),
    ("パンプス ポインテッドトゥ",         "HEEL工房",      "ヌード",     11800, 15, False, 4),
    ("デッキシューズ",                    "MARINE靴社",    "ネイビー",   7800,  22, False, 4),
    ("ランニングシューズ クッション",     "RUN工房",       "ライムグリーン", 9200, 20, True, 4),
    ("ウォーキングシューズ 幅広",         "WALK靴社",      "グレー",     8500,  18, False, 4),
    ("モカシン スエード",                 "MOCA工房",      "キャメル",   7200,  20, False, 4),
    ("ミュール ヒール付き",               "MULE靴社",      "ホワイト",   8800,  15, False, 4),
    ("トレッキングシューズ",              "MOUNTAIN工房",  "オリーブ",   14800, 12, True,  4),
    ("バレエシューズ フラット",           "DANCE靴社",     "ブラック",   5500,  30, False, 4),
    ("アンクルブーツ レザー",            "BOOT工房",      "ブラウン",   13800, 10, True,  4),

    # アクセサリー (category_id=5)
    ("シルバーリング シンプル",           "SILVER工房",    "シルバー",   3200,  40, False, 5),
    ("パールネックレス 淡水",             "PEARL社",       "ホワイト",   8800,  20, True,  5),
    ("レザーブレスレット",                "LEATHER工房",   "ブラウン",   2800,  35, False, 5),
    ("ゴールドフープイヤリング",          "GOLD社",        "ゴールド",   4500,  30, True,  5),
    ("シルクスカーフ 正方形",             "SILK工房",      "マルチカラー", 6800, 20, False, 5),
    ("アンティーク調ブローチ",            "BROOCH社",      "ゴールド",   3800,  25, False, 5),
    ("皮革手袋 スマホ対応",              "GLOVE工房",     "ブラック",   5500,  18, True,  5),
    ("ウールマフラー チェック",           "SCARF社",       "レッド×グレー", 4200, 30, False, 5),
    ("サングラス スクエア型",             "SUN工房",       "ブラック",   7800,  22, True,  5),
    ("ヘアバンド リボン付き",             "HAIR社",        "ブラック",   1800,  50, False, 5),
    ("チタンリング",                      "TITAN工房",     "シルバー",   5800,  20, False, 5),
    ("天然石ブレスレット",               "STONE社",       "パープル",   4200,  28, True,  5),
    ("レザーベルト ゴールドバックル",    "BELT工房",      "ブラウン",   5200,  25, False, 5),
    ("ニットヘアバンド",                  "KNIT社",        "ベージュ",   1500,  60, False, 5),
    ("アクリルバングル セット",           "BANGLE工房",    "クリア",     2800,  35, False, 5),
]

# ══════════════════════════════════════════════
# generate_colorful_items.py の商品データ（20件, ID: 280〜299）
# ══════════════════════════════════════════════
COLORFUL_ITEMS = [
    ("ポップカラートートバッグ",     "VIVID工房",   "イエロー",          3800, 30, False, 1),
    ("レインボーバックパック",        "COLOR社",     "レインボー",        5200, 20, True,  1),
    ("コーラルピンクポーチ",         "PASTEL工房",  "コーラルピンク",    2200, 40, False, 1),
    ("エレクトリックブルークラッチ",  "NEON社",      "エレクトリックブルー", 3500, 25, False, 1),

    ("ホットピンクベレー帽",         "VIVID帽子社", "ホットピンク",      2800, 35, False, 2),
    ("イエローグリーンキャップ",     "NEON工房",    "イエローグリーン",  3200, 28, True,  2),
    ("オレンジバケットハット",       "COLOR帽子社", "オレンジ",          2500, 40, False, 2),

    ("ラベンダースウェット",         "PASTEL工房",  "ラベンダー",        4500, 30, False, 3),
    ("マゼンタTシャツ",             "BOLD社",      "マゼンタ",          2200, 50, False, 3),
    ("コバルトブルーニットセーター", "VIVID工房",   "コバルトブルー",    7800, 18, True,  3),
    ("ライムグリーンジャケット",     "COLOR社",     "ライムグリーン",    8500, 15, True,  3),
    ("サンセットオレンジワンピース", "SUNSET工房",  "オレンジ×ピンク",  6800, 20, False, 3),
    ("タイダイパターンTシャツ",     "TIE工房",     "マルチカラー",      3200, 35, False, 3),
    ("ターコイズブルーカーディガン", "VIVID社",     "ターコイズ",        6200, 22, False, 3),

    ("ネオングリーンスニーカー",     "NEON靴社",    "ネオングリーン",    7200, 20, True,  4),
    ("コーラルサンダル",            "COLOR靴工房", "コーラル",          5500, 25, False, 4),
    ("パープルハイカットスニーカー", "VIVID靴社",   "パープル",          8800, 15, True,  4),

    ("カラフルビーズブレスレット",  "BEAD工房",    "マルチカラー",      1800, 60, False, 5),
    ("エメラルドグリーンピアス",    "GEM社",       "エメラルドグリーン", 4800, 25, True,  5),
    ("サンセットイヤリング",        "SUNSET工房",  "オレンジ×イエロー", 3500, 30, False, 5),
]


def find_image_for_id(item_id, media_items_dir):
    """item_id に一致する画像ファイルを検索"""
    prefix = f"item_{item_id}_"
    for filepath in media_items_dir.iterdir():
        if filepath.name.startswith(prefix):
            return filepath.name
    return None


def main():
    media_items_dir = BASE_DIR / 'media' / 'items'

    if not media_items_dir.exists():
        print("❌ media/items/ ディレクトリが見つかりません")
        return

    # ── Step 1: カテゴリを登録 ──
    print("=" * 60)
    print("Step 1: カテゴリ登録")
    print("=" * 60)
    for category_id, name in CATEGORIES_DATA:
        obj, created = Category.objects.update_or_create(
            category_id=category_id,
            defaults={"name": name},
        )
        status = "新規作成" if created else "既存"
        print(f"  [{category_id}] {status}: {name}")

    # ── Step 2: 既存商品をすべてクリア ──
    print()
    print("=" * 60)
    print("Step 2: 既存商品をクリア")
    print("=" * 60)
    deleted_count, _ = Item.objects.all().delete()
    print(f"  🗑️  {deleted_count}件削除しました")

    # ── Step 3: 商品＋画像を一括登録 ──
    print()
    print("=" * 60)
    print("Step 3: 画像付き商品を登録")
    print("=" * 60)

    all_items = [(200 + i, *data) for i, data in enumerate(ITEMS_DATA)]
    all_items += [(280 + i, *data) for i, data in enumerate(COLORFUL_ITEMS)]

    created_count = 0
    image_linked = 0
    no_image_count = 0

    for item_id, name, manufacturer, color, price, stock, recommended, cat_id in all_items:
        category = Category.objects.get(category_id=cat_id)

        image_filename = find_image_for_id(item_id, media_items_dir)
        image_path = f"items/{image_filename}" if image_filename else ""

        Item.objects.create(
            item_id=item_id,
            name=name,
            manufacturer=manufacturer,
            color=color,
            price=price,
            stock=stock,
            recommended=recommended,
            category=category,
            image=image_path,
        )

        created_count += 1
        if image_filename:
            image_linked += 1
            print(f"  [{item_id}] ✅ {name}  📷 {image_filename}")
        else:
            no_image_count += 1
            print(f"  [{item_id}] ✅ {name}  ⚠️ 画像なし")

    print()
    print("=" * 60)
    print(f"✅ 登録完了:   {created_count}件")
    print(f"📷 画像あり:   {image_linked}件")
    print(f"⚠️  画像なし:   {no_image_count}件")
    print("=" * 60)


if __name__ == '__main__':
    main()