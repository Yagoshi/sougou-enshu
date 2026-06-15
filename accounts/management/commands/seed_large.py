# -*- coding: utf-8 -*-
"""
サンプルデータ投入コマンド（大量データ版：各テーブル50件）

配置場所:
    accounts/management/commands/seed_large.py

実行方法:
    python manage.py seed_large            # データ投入(既存データはスキップ/更新)
    python manage.py seed_large --clear    # 全削除してから投入
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.apps import apps


class SeedDefinitionError(CommandError):
    """サンプルデータ投入に必要なモデル/属性の定義が不足している場合に送出する例外。"""
    pass


class Command(BaseCommand):
    help = "各テーブルにサンプルデータ(約50件ずつ)を投入します"

    REQUIRED_TABLES = {
        "account_user": {
            "alias": "Account",
            "fields": ["user_id", "password", "name", "address"],
        },
        "shopping_category": {
            "alias": "Category",
            "fields": ["category_id", "name"],
        },
        "shopping_item": {
            "alias": "Item",
            "fields": ["item_id", "name", "manufacturer", "color", "price", "stock", "recommended", "category"],
        },
        "shopping_itemsincart": {
            "alias": "Itemincart",
            "fields": ["amount", "booked_date", "item", "user"],
        },
        "shopping_purchase": {
            "alias": "Purchase",
            "fields": ["purchase_id", "destination", "booked_date", "cancel", "user"],
        },
        "shopping_purchasedetail": {
            "alias": "Purchasedetail",
            "fields": ["purchase_detail_id", "amount", "item", "purchase"],
        },
        "administrator_admin": {
            "alias": "Admin",
            "fields": ["admin_id", "password"],
        },
    }

    def load_models(self):
        model_map = {
            model._meta.db_table: model
            for model in apps.get_models()
        }

        missing_tables = []
        missing_fields = []

        for table_name, info in self.REQUIRED_TABLES.items():
            model = model_map.get(table_name)

            if model is None:
                missing_tables.append(table_name)
                continue

            model_fields = {
                field.name
                for field in model._meta.get_fields()
            }

            for field_name in info["fields"]:
                if field_name not in model_fields:
                    missing_fields.append((table_name, field_name))

        if missing_tables or missing_fields:
            messages = []

            for table_name in missing_tables:
                messages.append(
                    f"テーブル名：{table_name} に対応するモデルが定義されていません。"
                )

            for table_name, field_name in missing_fields:
                messages.append(
                    f"テーブル名：{table_name} に属性名：{field_name} が定義されていません。"
                )

            raise SeedDefinitionError(
                "サンプルデータの投入に必要なモデル定義が不足しています。\n"
                + "\n".join(messages)
            )

        return {
            info["alias"]: model_map[table_name]
            for table_name, info in self.REQUIRED_TABLES.items()
        }

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="投入前に既存データをすべて削除する",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        models = self.load_models()

        Account = models["Account"]
        Category = models["Category"]
        Item = models["Item"]
        Itemincart = models["Itemincart"]
        Purchase = models["Purchase"]
        Purchasedetail = models["Purchasedetail"]
        Admin = models["Admin"]

        if options["clear"]:
            self.stdout.write("既存データを削除しています...")
            # 外部キー制約を考慮して子テーブルから削除
            Purchasedetail.objects.all().delete()
            Purchase.objects.all().delete()
            Itemincart.objects.all().delete()
            Item.objects.all().delete()
            Category.objects.all().delete()
            Account.objects.all().delete()
            Admin.objects.all().delete()

        # ====================================
        # 会員 (account_user) - 50件
        # ====================================
        accounts_data = [
            ('user001', 'password001', '斎藤 美咲', '東京都新宿区西新宿5-4-4'),
            ('user002', 'password002', '高橋 美咲', '神奈川県横浜市西区みなとみらい2-7-1'),
            ('user003', 'password003', '山田 一郎', '福岡県福岡市博多区博多駅前4-9-1'),
            ('user004', 'password004', '山口 由美', '神奈川県横浜市西区みなとみらい7-4-8'),
            ('user005', 'password005', '池田 愛', '東京都新宿区西新宿3-7-6'),
            ('user006', 'password006', '小林 健太', '福岡県福岡市博多区博多駅前6-2-2'),
            ('user007', 'password007', '松本 美咲', '宮城県仙台市青葉区中央6-5-1'),
            ('user008', 'password008', '石川 彩', '神奈川県横浜市西区みなとみらい2-7-2'),
            ('user009', 'password009', '山口 大輔', '兵庫県神戸市中央区三宮町6-4-2'),
            ('user010', 'password010', '佐藤 翔', '北海道札幌市中央区大通西2-4-2'),
            ('user011', 'password011', '松本 愛', '京都府京都市下京区四条通6-3-6'),
            ('user012', 'password012', '山本 由美', '北海道札幌市中央区大通西2-3-9'),
            ('user013', 'password013', '石川 翔', '愛知県名古屋市中区栄8-7-5'),
            ('user014', 'password014', '村上 裕子', '福岡県福岡市博多区博多駅前6-1-4'),
            ('user015', 'password015', '藤田 花子', '宮城県仙台市青葉区中央7-5-2'),
            ('user016', 'password016', '伊藤 聡', '宮城県仙台市青葉区中央4-8-7'),
            ('user017', 'password017', '長谷川 彩', '愛知県名古屋市中区栄5-3-4'),
            ('user018', 'password018', '石川 裕子', '神奈川県横浜市西区みなとみらい5-7-7'),
            ('user019', 'password019', '山本 翔', '愛知県名古屋市中区栄9-8-2'),
            ('user020', 'password020', '中島 花子', '大阪府大阪市北区梅田3-3-7'),
            ('user021', 'password021', '橋本 一郎', '広島県広島市中区紙屋町7-8-9'),
            ('user022', 'password022', '小林 裕子', '東京都新宿区西新宿2-9-5'),
            ('user023', 'password023', '中島 結衣', '大阪府大阪市北区梅田5-7-3'),
            ('user024', 'password024', '木村 太郎', '北海道札幌市中央区大通西9-3-9'),
            ('user025', 'password025', '村上 美咲', '北海道札幌市中央区大通西9-4-3'),
            ('user026', 'password026', '山本 直樹', '神奈川県横浜市西区みなとみらい9-1-6'),
            ('user027', 'password027', '林 太郎', '大阪府大阪市北区梅田6-5-4'),
            ('user028', 'password028', '佐藤 翔', '兵庫県神戸市中央区三宮町2-2-8'),
            ('user029', 'password029', '藤田 一郎', '神奈川県横浜市西区みなとみらい3-3-8'),
            ('user030', 'password030', '山口 直樹', '北海道札幌市中央区大通西9-7-4'),
            ('user031', 'password031', '村上 裕子', '福岡県福岡市博多区博多駅前5-7-6'),
            ('user032', 'password032', '木村 薫', '京都府京都市下京区四条通2-4-4'),
            ('user033', 'password033', '鈴木 結衣', '東京都新宿区西新宿9-4-4'),
            ('user034', 'password034', '山田 一郎', '東京都新宿区西新宿4-2-1'),
            ('user035', 'password035', '岡田 結衣', '大阪府大阪市北区梅田9-4-5'),
            ('user036', 'password036', '佐々木 健', '福岡県福岡市博多区博多駅前9-3-8'),
            ('user037', 'password037', '中村 健', '広島県広島市中区紙屋町4-2-2'),
            ('user038', 'password038', '佐々木 純一', '宮城県仙台市青葉区中央7-7-8'),
            ('user039', 'password039', '岡田 花子', '大阪府大阪市北区梅田1-7-6'),
            ('user040', 'password040', '前田 美咲', '福岡県福岡市博多区博多駅前4-4-9'),
            ('user041', 'password041', '木村 健太', '広島県広島市中区紙屋町3-5-8'),
            ('user042', 'password042', '中村 一郎', '京都府京都市下京区四条通9-2-1'),
            ('user043', 'password043', '斎藤 裕子', '東京都新宿区西新宿2-4-3'),
            ('user044', 'password044', '井上 健', '京都府京都市下京区四条通4-7-1'),
            ('user045', 'password045', '渡辺 真理', '東京都新宿区西新宿7-5-8'),
            ('user046', 'password046', '加藤 純一', '神奈川県横浜市西区みなとみらい8-3-4'),
            ('user047', 'password047', '加藤 由美', '東京都新宿区西新宿9-1-6'),
            ('user048', 'password048', '佐藤 花子', '兵庫県神戸市中央区三宮町8-9-9'),
            ('user049', 'password049', '渡辺 花子', '神奈川県横浜市西区みなとみらい2-3-2'),
            ('user050', 'password050', '橋本 一郎', '福岡県福岡市博多区博多駅前7-2-4'),
        ]
        accounts = {}
        for user_id, password, name, address in accounts_data:
            obj, created = Account.objects.update_or_create(
                user_id=user_id,
                defaults={
                    "password": password,
                    "name": name,
                    "address": address,
                },
            )
            accounts[user_id] = obj
        self.stdout.write(self.style.SUCCESS(f"会員: {len(accounts)}件"))

        # ====================================
        # カテゴリ (shopping_category)
        # ====================================
        categories_data = [
            (1, '鞄'),
            (2, '帽子'),
            (3, '靴'),
            (4, 'アクセサリー'),
            (5, 'アウター'),
            (6, '雑貨'),
        ]
        categories = {}
        for category_id, name in categories_data:
            obj, created = Category.objects.update_or_create(
                category_id=category_id,
                defaults={"name": name},
            )
            categories[category_id] = obj
        self.stdout.write(self.style.SUCCESS(f"カテゴリ: {len(categories)}件"))

        # ====================================
        # 商品 (shopping_item) - 50件
        # ====================================
        items_data = [
            # (item_id, name, manufacturer, color, price, stock, recommended, category_id)
            (101, 'レザーハンドバッグ エレガント', 'アウターズギルド', 'ピンク', 9800, 10, False, 1),
            (102, 'キャンバストートバッグ L', 'フットウェアラボ', 'ネイビー', 9800, 71, False, 1),
            (103, '撥水リュック 25L', 'アウターズギルド', 'ベージュ', 12800, 45, True, 1),
            (104, '2WAYショルダーバッグ', 'ダミーバッグ社', 'ブラック', 12800, 43, False, 1),
            (105, 'ミニマルクラッチバッグ', 'ダミーバッグ社', 'ナチュラル', 6480, 77, False, 1),
            (106, 'ビジネスブリーフケース', 'アクセサリーミライ', 'ブラウン', 3280, 69, False, 1),
            (107, '折り畳みエコバッグ', 'リビングテストグッズ', 'ナチュラル', 3280, 52, False, 1),
            (108, 'ボストンバッグ 大容量', 'ノーブランド商会', 'ブラック', 15800, 43, False, 1),
            (109, 'ウエストポーチ', 'ダミーバッグ社', 'ベージュ', 12800, 75, False, 1),
            (110, 'コットンキャップ ロゴ刺繍', 'ノーブランド商会', 'ベージュ', 3980, 19, False, 2),
            (111, 'つば広ストローハット', 'アクセサリーミライ', 'ネイビー', 3980, 41, False, 2),
            (112, 'ニットビーニー', 'フットウェアラボ', 'ブラック', 12800, 38, False, 2),
            (113, 'バケットハット', 'サンプルレザー工房', 'ブラック', 2480, 59, False, 2),
            (114, 'ウールフェルトハット', 'フットウェアラボ', 'ベージュ', 4980, 21, False, 2),
            (115, 'サンバイザー スポーツ用', 'アウターズギルド', 'ナチュラル', 15800, 61, False, 2),
            (116, 'ハンチング帽', 'テストアウトドア', 'ナチュラル', 1980, 19, True, 2),
            (117, 'キャスケット風帽子', 'テストアウトドア', 'レッド', 1980, 52, False, 2),
            (118, 'レザースニーカー', 'サンプルレザー工房', 'グレー', 2980, 10, False, 3),
            (119, '防水ウォーキングシューズ', 'アクセサリーミライ', 'ナチュラル', 3280, 36, False, 3),
            (120, 'ローファー クラシック', '帽子サンプル堂', 'ベージュ', 5980, 24, False, 3),
            (121, 'サンダル コンフォート', 'サンプルレザー工房', 'ベージュ', 19800, 27, False, 3),
            (122, 'ブーツ ショート丈', 'アウターズギルド', 'ネイビー', 15800, 47, False, 3),
            (123, 'ランニングシューズ エア', 'ダミーバッグ社', 'レッド', 3980, 25, False, 3),
            (124, 'パンプス ベーシック', 'リビングテストグッズ', 'グレー', 1980, 65, True, 3),
            (125, 'スリッポン キャンバス', '帽子サンプル堂', 'レッド', 3980, 34, True, 3),
            (126, 'シルバーネックレス シンプル', 'フットウェアラボ', 'グレー', 4980, 40, False, 4),
            (127, 'レザーベルト ブラウン', 'ノーブランド商会', 'グレー', 12800, 70, False, 4),
            (128, 'サングラス UVカット', 'フットウェアラボ', 'ベージュ', 1980, 19, False, 4),
            (129, '腕時計 アナログ', 'クラフトワークス', 'レッド', 9800, 38, True, 4),
            (130, 'マフラー カシミア混', 'ノーブランド商会', 'ブラウン', 4980, 45, False, 4),
            (131, '手袋 レザー', 'サンプルレザー工房', 'レッド', 5980, 78, True, 4),
            (132, 'ピアス パール調', 'ノーブランド商会', 'ネイビー', 1980, 71, False, 4),
            (133, 'ヘアアクセサリー セット', 'アクセサリーミライ', 'ピンク', 4980, 60, True, 4),
            (134, 'ブレスレット チェーン', 'フットウェアラボ', 'ナチュラル', 4980, 20, False, 4),
            (135, 'ダウンジャケット ライト', 'フットウェアラボ', 'ナチュラル', 3980, 57, False, 5),
            (136, 'トレンチコート ベーシック', 'アウターズギルド', 'ベージュ', 2980, 29, False, 5),
            (137, 'ウィンドブレーカー', 'ノーブランド商会', 'ブラック', 9800, 77, False, 5),
            (138, 'ニットカーディガン', 'クラフトワークス', 'ピンク', 3980, 41, True, 5),
            (139, 'デニムジャケット', 'リビングテストグッズ', 'ネイビー', 12800, 46, False, 5),
            (140, 'フリースジャケット', 'テストアウトドア', 'ブラウン', 7980, 65, False, 5),
            (141, 'マウンテンパーカー', 'クラフトワークス', 'グレー', 3980, 70, False, 5),
            (142, 'テーラードジャケット', '帽子サンプル堂', 'ネイビー', 2480, 35, False, 5),
            (143, '折り畳み傘 軽量', 'リビングテストグッズ', 'ピンク', 2980, 8, True, 6),
            (144, 'タンブラー ステンレス', 'クラフトワークス', 'ネイビー', 19800, 14, False, 6),
            (145, 'ポーチ 多機能', '帽子サンプル堂', 'ベージュ', 15800, 54, False, 6),
            (146, 'モバイルバッテリー 大容量', 'ダミーバッグ社', 'レッド', 12800, 5, False, 6),
            (147, 'ブランケット フリース', 'ノーブランド商会', 'カーキ', 3280, 27, False, 6),
            (148, 'コインケース レザー', 'ダミーバッグ社', 'カーキ', 1980, 76, True, 6),
            (149, 'アイマスク 旅行用', 'ノーブランド商会', 'ピンク', 2980, 64, False, 6),
            (150, 'ネックピロー', 'ノーブランド商会', 'レッド', 4980, 61, False, 6),
        ]
        items = {}
        for item_id, name, manufacturer, color, price, stock, recommended, cat_id in items_data:
            obj, created = Item.objects.update_or_create(
                item_id=item_id,
                defaults={
                    "name": name,
                    "manufacturer": manufacturer,
                    "color": color,
                    "price": price,
                    "stock": stock,
                    "recommended": recommended,
                    "category": categories[cat_id],
                },
            )
            items[item_id] = obj
        self.stdout.write(self.style.SUCCESS(f"商品: {len(items)}件"))

        # ====================================
        # カート内商品 (shopping_itemsincart) - 50件
        # ※ booked_date は auto_now_add のため実行時刻が入ります
        # ====================================
        cart_data = [
            # (amount, item_id, user_id)
            (4, 101, 'user001'),
            (2, 104, 'user002'),
            (4, 107, 'user003'),
            (4, 110, 'user004'),
            (3, 113, 'user005'),
            (2, 116, 'user006'),
            (3, 119, 'user007'),
            (4, 122, 'user008'),
            (2, 125, 'user009'),
            (3, 128, 'user010'),
            (4, 131, 'user011'),
            (1, 134, 'user012'),
            (3, 137, 'user013'),
            (2, 140, 'user014'),
            (3, 143, 'user015'),
            (3, 146, 'user016'),
            (3, 149, 'user017'),
            (1, 102, 'user018'),
            (2, 105, 'user019'),
            (2, 108, 'user020'),
            (2, 111, 'user021'),
            (4, 114, 'user022'),
            (2, 117, 'user023'),
            (2, 120, 'user024'),
            (1, 123, 'user025'),
            (4, 126, 'user026'),
            (4, 129, 'user027'),
            (3, 132, 'user028'),
            (4, 135, 'user029'),
            (4, 138, 'user030'),
            (1, 141, 'user031'),
            (2, 144, 'user032'),
            (4, 147, 'user033'),
            (4, 150, 'user034'),
            (1, 103, 'user035'),
            (4, 106, 'user036'),
            (4, 109, 'user037'),
            (1, 112, 'user038'),
            (3, 115, 'user039'),
            (3, 118, 'user040'),
            (4, 121, 'user041'),
            (4, 124, 'user042'),
            (2, 127, 'user043'),
            (4, 130, 'user044'),
            (2, 133, 'user045'),
            (3, 136, 'user046'),
            (4, 139, 'user047'),
            (4, 142, 'user048'),
            (1, 145, 'user049'),
            (4, 148, 'user050'),
        ]
        # 重複投入を避けるため一旦削除してから作成
        Itemincart.objects.all().delete()
        cart_objs = [
            Itemincart(amount=amount, item=items[item_id], user=accounts[user_id])
            for amount, item_id, user_id in cart_data
        ]
        Itemincart.objects.bulk_create(cart_objs)
        self.stdout.write(self.style.SUCCESS(f"カート内商品: {len(cart_objs)}件"))

        # ====================================
        # 注文 (shopping_purchase) - 50件
        # ====================================
        purchases_data = [
            # (purchase_id, destination, cancel, user_id)
            (1001, '東京都新宿区西新宿5-4-4', False, 'user001'),
            (1002, '神奈川県横浜市西区みなとみらい2-7-1', False, 'user002'),
            (1003, '福岡県福岡市博多区博多駅前4-9-1', False, 'user003'),
            (1004, '神奈川県横浜市西区みなとみらい7-4-8', False, 'user004'),
            (1005, '東京都新宿区西新宿3-7-6', False, 'user005'),
            (1006, '福岡県福岡市博多区博多駅前6-2-2', False, 'user006'),
            (1007, '宮城県仙台市青葉区中央6-5-1', True, 'user007'),
            (1008, '神奈川県横浜市西区みなとみらい2-7-2', False, 'user008'),
            (1009, '兵庫県神戸市中央区三宮町6-4-2', False, 'user009'),
            (1010, '北海道札幌市中央区大通西2-4-2', False, 'user010'),
            (1011, '京都府京都市下京区四条通6-3-6', False, 'user011'),
            (1012, '北海道札幌市中央区大通西2-3-9', False, 'user012'),
            (1013, '愛知県名古屋市中区栄8-7-5', False, 'user013'),
            (1014, '福岡県福岡市博多区博多駅前6-1-4', False, 'user014'),
            (1015, '宮城県仙台市青葉区中央7-5-2', False, 'user015'),
            (1016, '宮城県仙台市青葉区中央4-8-7', False, 'user016'),
            (1017, '愛知県名古屋市中区栄5-3-4', False, 'user017'),
            (1018, '神奈川県横浜市西区みなとみらい5-7-7', False, 'user018'),
            (1019, '愛知県名古屋市中区栄9-8-2', True, 'user019'),
            (1020, '大阪府大阪市北区梅田3-3-7', False, 'user020'),
            (1021, '広島県広島市中区紙屋町7-8-9', False, 'user021'),
            (1022, '東京都新宿区西新宿2-9-5', False, 'user022'),
            (1023, '大阪府大阪市北区梅田5-7-3', False, 'user023'),
            (1024, '北海道札幌市中央区大通西9-3-9', False, 'user024'),
            (1025, '北海道札幌市中央区大通西9-4-3', False, 'user025'),
            (1026, '神奈川県横浜市西区みなとみらい9-1-6', False, 'user026'),
            (1027, '大阪府大阪市北区梅田6-5-4', False, 'user027'),
            (1028, '兵庫県神戸市中央区三宮町2-2-8', False, 'user028'),
            (1029, '神奈川県横浜市西区みなとみらい3-3-8', False, 'user029'),
            (1030, '北海道札幌市中央区大通西9-7-4', False, 'user030'),
            (1031, '福岡県福岡市博多区博多駅前5-7-6', False, 'user031'),
            (1032, '京都府京都市下京区四条通2-4-4', False, 'user032'),
            (1033, '東京都新宿区西新宿9-4-4', False, 'user033'),
            (1034, '東京都新宿区西新宿4-2-1', False, 'user034'),
            (1035, '大阪府大阪市北区梅田9-4-5', False, 'user035'),
            (1036, '福岡県福岡市博多区博多駅前9-3-8', False, 'user036'),
            (1037, '広島県広島市中区紙屋町4-2-2', False, 'user037'),
            (1038, '宮城県仙台市青葉区中央7-7-8', False, 'user038'),
            (1039, '大阪府大阪市北区梅田1-7-6', False, 'user039'),
            (1040, '福岡県福岡市博多区博多駅前4-4-9', False, 'user040'),
            (1041, '広島県広島市中区紙屋町3-5-8', False, 'user041'),
            (1042, '京都府京都市下京区四条通9-2-1', False, 'user042'),
            (1043, '東京都新宿区西新宿2-4-3', False, 'user043'),
            (1044, '京都府京都市下京区四条通4-7-1', False, 'user044'),
            (1045, '東京都新宿区西新宿7-5-8', False, 'user045'),
            (1046, '神奈川県横浜市西区みなとみらい8-3-4', False, 'user046'),
            (1047, '東京都新宿区西新宿9-1-6', False, 'user047'),
            (1048, '兵庫県神戸市中央区三宮町8-9-9', False, 'user048'),
            (1049, '神奈川県横浜市西区みなとみらい2-3-2', False, 'user049'),
            (1050, '福岡県福岡市博多区博多駅前7-2-4', False, 'user050'),
        ]
        purchases = {}
        for purchase_id, destination, cancel, user_id in purchases_data:
            obj, created = Purchase.objects.update_or_create(
                purchase_id=purchase_id,
                defaults={
                    "destination": destination,
                    "cancel": cancel,
                    "user": accounts[user_id],
                },
            )
            purchases[purchase_id] = obj
        self.stdout.write(self.style.SUCCESS(f"注文: {len(purchases)}件"))

        # ====================================
        # 注文詳細 (shopping_purchasedetail) - 50件
        # ====================================
        details_data = [
            # (purchase_detail_id, amount, item_id, purchase_id)
            (10001, 3, 101, 1001),
            (10002, 3, 108, 1002),
            (10003, 2, 115, 1003),
            (10004, 3, 122, 1004),
            (10005, 2, 129, 1005),
            (10006, 3, 136, 1006),
            (10007, 3, 143, 1007),
            (10008, 2, 150, 1008),
            (10009, 2, 107, 1009),
            (10010, 1, 114, 1010),
            (10011, 2, 121, 1011),
            (10012, 2, 128, 1012),
            (10013, 2, 135, 1013),
            (10014, 1, 142, 1014),
            (10015, 3, 149, 1015),
            (10016, 2, 106, 1016),
            (10017, 1, 113, 1017),
            (10018, 3, 120, 1018),
            (10019, 1, 127, 1019),
            (10020, 1, 134, 1020),
            (10021, 3, 141, 1021),
            (10022, 1, 148, 1022),
            (10023, 1, 105, 1023),
            (10024, 1, 112, 1024),
            (10025, 2, 119, 1025),
            (10026, 1, 126, 1026),
            (10027, 3, 133, 1027),
            (10028, 1, 140, 1028),
            (10029, 1, 147, 1029),
            (10030, 2, 104, 1030),
            (10031, 2, 111, 1031),
            (10032, 3, 118, 1032),
            (10033, 3, 125, 1033),
            (10034, 3, 132, 1034),
            (10035, 3, 139, 1035),
            (10036, 3, 146, 1036),
            (10037, 1, 103, 1037),
            (10038, 3, 110, 1038),
            (10039, 2, 117, 1039),
            (10040, 3, 124, 1040),
            (10041, 3, 131, 1041),
            (10042, 1, 138, 1042),
            (10043, 2, 145, 1043),
            (10044, 2, 102, 1044),
            (10045, 2, 109, 1045),
            (10046, 2, 116, 1046),
            (10047, 3, 123, 1047),
            (10048, 2, 130, 1048),
            (10049, 3, 137, 1049),
            (10050, 2, 144, 1050),
        ]
        for detail_id, amount, item_id, purchase_id in details_data:
            Purchasedetail.objects.update_or_create(
                purchase_detail_id=detail_id,
                defaults={
                    "amount": amount,
                    "item": items[item_id],
                    "purchase": purchases[purchase_id],
                },
            )
        self.stdout.write(self.style.SUCCESS(f"注文詳細: {len(details_data)}件"))

        # ====================================
        # 管理者 (administrator_admin) - 50件
        # ====================================
        admins_data = [
            ('admin001', 'adminpass001'),
            ('admin002', 'adminpass002'),
            ('admin003', 'adminpass003'),
            ('admin004', 'adminpass004'),
            ('admin005', 'adminpass005'),
            ('admin006', 'adminpass006'),
            ('admin007', 'adminpass007'),
            ('admin008', 'adminpass008'),
            ('admin009', 'adminpass009'),
            ('admin010', 'adminpass010'),
            ('admin011', 'adminpass011'),
            ('admin012', 'adminpass012'),
            ('admin013', 'adminpass013'),
            ('admin014', 'adminpass014'),
            ('admin015', 'adminpass015'),
            ('admin016', 'adminpass016'),
            ('admin017', 'adminpass017'),
            ('admin018', 'adminpass018'),
            ('admin019', 'adminpass019'),
            ('admin020', 'adminpass020'),
            ('admin021', 'adminpass021'),
            ('admin022', 'adminpass022'),
            ('admin023', 'adminpass023'),
            ('admin024', 'adminpass024'),
            ('admin025', 'adminpass025'),
            ('admin026', 'adminpass026'),
            ('admin027', 'adminpass027'),
            ('admin028', 'adminpass028'),
            ('admin029', 'adminpass029'),
            ('admin030', 'adminpass030'),
            ('admin031', 'adminpass031'),
            ('admin032', 'adminpass032'),
            ('admin033', 'adminpass033'),
            ('admin034', 'adminpass034'),
            ('admin035', 'adminpass035'),
            ('admin036', 'adminpass036'),
            ('admin037', 'adminpass037'),
            ('admin038', 'adminpass038'),
            ('admin039', 'adminpass039'),
            ('admin040', 'adminpass040'),
            ('admin041', 'adminpass041'),
            ('admin042', 'adminpass042'),
            ('admin043', 'adminpass043'),
            ('admin044', 'adminpass044'),
            ('admin045', 'adminpass045'),
            ('admin046', 'adminpass046'),
            ('admin047', 'adminpass047'),
            ('admin048', 'adminpass048'),
            ('admin049', 'adminpass049'),
            ('admin050', 'adminpass050'),
        ]
        for admin_id, raw_password in admins_data:
            Admin.objects.update_or_create(
                admin_id=admin_id,
                defaults={"password": make_password(raw_password)},
            )
        self.stdout.write(self.style.SUCCESS(f"管理者: {len(admins_data)}件"))

        self.stdout.write(self.style.SUCCESS("=== サンプルデータ(50件規模)の投入が完了しました ==="))
