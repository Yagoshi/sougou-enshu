# -*- coding: utf-8 -*-
"""
サンプルデータ投入コマンド

配置場所:
    <アプリ名>/management/commands/seed.py

実行方法:
    python manage.py seed            # データ投入(既存データはスキップ/更新)
    python manage.py seed --clear    # 全削除してから投入

※ カテゴリ・商品は register_items_with_images.py で登録してください。
"""
import random
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.apps import apps


class SeedDefinitionError(CommandError):
    """サンプルデータ投入に必要なモデル/属性の定義が不足している場合に送出する例外。"""
    pass


class Command(BaseCommand):
    help = "会員・注文・管理者・評価データのサンプルデータを投入します"

    REQUIRED_TABLES = {
        "account_user": {
            "alias": "Account",
            "fields": ["user_id", "password", "name", "address"],
        },
        "shopping_item": {
            "alias": "Item",
            "fields": ["item_id", "recommended"],
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
        "shopping_review": {
            "alias": "Review",
            "fields": ["rating", "title", "comment", "helpful_count",
                       "is_verified_purchase", "item", "user"],
        },
    }

    # ── レビューテンプレート（評価点ごと） ──
    REVIEW_TEMPLATES = {
        5: [
            ("最高の買い物でした！",   "品質が素晴らしく、届いてすぐに気に入りました。また購入したいです。"),
            ("大満足です",             "デザインも品質も期待以上でした。友人にも勧めたいと思います。"),
            ("これは買いです！",       "コスパが非常に高く、毎日愛用しています。本当に買ってよかった。"),
            ("完璧な商品",             "細部まで丁寧に作られており、長く使えそうです。とても気に入っています。"),
            ("リピート確定です",       "前回も購入しましたが、今回も期待通りでした。品質が安定していて信頼できます。"),
        ],
        4: [
            ("とても良い商品です",     "品質が良く満足しています。少し配送に時間がかかりましたが商品自体は問題なし。"),
            ("おすすめできます",       "全体的に満足です。若干気になる点もありますが、値段を考えれば十分です。"),
            ("良い買い物でした",       "写真通りの商品が届きました。実用的で使いやすいです。"),
            ("概ね満足",               "品質は良いです。細かい部分が気になりましたが、総合的には満足しています。"),
            ("なかなか良いです",       "使いやすく、見た目もおしゃれです。もう少し安ければ星5でした。"),
        ],
        3: [
            ("普通です",               "可もなく不可もなくといった印象です。値段相応だと思います。"),
            ("まあまあ",               "特に問題はないのですが、期待していたほどではありませんでした。"),
            ("悪くはないです",         "品質は標準的です。もう少し改善があればもっと良いと思います。"),
            ("可もなく不可もなく",     "使い勝手は普通です。特に感動もなく、不満もないといった感じです。"),
            ("標準的な商品",           "説明通りの商品です。特段優れている点も劣っている点もありません。"),
        ],
        2: [
            ("期待外れでした",         "品質が思っていたより低く、少し残念です。もう少し丁寧な作りを期待していました。"),
            ("イマイチです",           "写真と実物が少し違う気がします。使えないことはないですが、満足度は低いです。"),
            ("改善を期待します",       "基本的な機能は果たしていますが、品質面で気になる点が多かったです。"),
        ],
        1: [
            ("残念でした",             "期待に応えてもらえませんでした。品質に問題があり、使い物になりませんでした。"),
            ("おすすめできません",     "品質が悪く返品を検討しています。商品説明と実物にかなり差がありました。"),
        ],
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
            model_fields = {f.name for f in model._meta.get_fields()}
            for field_name in info["fields"]:
                if field_name not in model_fields:
                    missing_fields.append((table_name, field_name))

        if missing_tables or missing_fields:
            messages = []
            for table_name in missing_tables:
                messages.append(f"テーブル名：{table_name} に対応するモデルが定義されていません。")
            for table_name, field_name in missing_fields:
                messages.append(f"テーブル名：{table_name} に属性名：{field_name} が定義されていません。")
            raise SeedDefinitionError(
                "サンプルデータの投入に必要なモデル定義が不足しています。\n" + "\n".join(messages)
            )

        return {info["alias"]: model_map[table_name] for table_name, info in self.REQUIRED_TABLES.items()}

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="投入前に既存データをすべて削除する（カテゴリ・商品は対象外）",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(42)
        models = self.load_models()

        Account     = models["Account"]
        Item        = models["Item"]
        Itemincart  = models["Itemincart"]
        Purchase    = models["Purchase"]
        Purchasedetail = models["Purchasedetail"]
        Admin       = models["Admin"]
        Review      = models["Review"]

        if options["clear"]:
            self.stdout.write("既存データを削除しています...")
            # 外部キー制約を考慮して子テーブルから削除（カテゴリ・商品は触らない）
            Review.objects.all().delete()
            Purchasedetail.objects.all().delete()
            Purchase.objects.all().delete()
            Itemincart.objects.all().delete()
            Account.objects.all().delete()
            Admin.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("削除完了"))

        # ====================================
        # 会員 (account_user)
        # ====================================
        accounts_data = [
            ("user001", "password001", "山田 太郎", "東京都新宿区西新宿1-1-1"),
            ("user002", "password002", "佐藤 花子", "大阪府大阪市北区梅田2-2-2"),
            ("user003", "password003", "鈴木 一郎", "愛知県名古屋市中区栄3-3-3"),
            ("user004", "password004", "田中 美咲", "福岡県福岡市博多区博多駅前4-4-4"),
            ("user005", "password005", "高橋 健太", "北海道札幌市中央区大通西5-5-5"),
        ]
        accounts = {}
        for user_id, password, name, address in accounts_data:
            obj, _ = Account.objects.update_or_create(
                user_id=user_id,
                defaults={"password": make_password(password), "name": name, "address": address},
            )
            accounts[user_id] = obj
        self.stdout.write(self.style.SUCCESS(f"会員: {len(accounts)}件"))

        # ====================================
        # カート内商品 (shopping_itemsincart)
        # カテゴリ・商品はregister_items_with_images.pyで登録済みの前提
        # ====================================
        items = {item.item_id: item for item in Item.objects.all()}
        if items:
            cart_data = [
                # (amount, item_id, user_id)
                (1, 200, "user001"),
                (3, 201, "user002"),
                (2, 202, "user003"),
                (1, 220, "user004"),
                (2, 250, "user005"),
            ]
            # 登録済みのitem_idのみ対象にフィルタ
            valid_cart_data = [(amt, iid, uid) for amt, iid, uid in cart_data if iid in items]
            Itemincart.objects.all().delete()
            cart_objs = [
                Itemincart(amount=amt, item=items[iid], user=accounts[uid])
                for amt, iid, uid in valid_cart_data
            ]
            Itemincart.objects.bulk_create(cart_objs)
            self.stdout.write(self.style.SUCCESS(f"カート内商品: {len(cart_objs)}件"))
        else:
            self.stdout.write(self.style.WARNING("商品が未登録のためカートデータはスキップしました"))

        # ====================================
        # 注文 (shopping_purchase)
        # ====================================
        purchases_data = [
            # (purchase_id, destination, cancel, user_id, payment_status, card_last4)
            (1001, "東京都新宿区西新宿1-1-1",       False, "user001", "succeeded", "4242"),
            (1002, "大阪府大阪市北区梅田2-2-2",       False, "user002", "succeeded", "4242"),
            (1003, "愛知県名古屋市中区栄3-3-3",       True,  "user003", "succeeded", "4242"),
            (1004, "福岡県福岡市博多区博多駅前4-4-4", False, "user004", "succeeded", "1234"),
            (1005, "北海道札幌市中央区大通西5-5-5",   False, "user005", "succeeded", "5678"),
        ]
        purchases = {}
        for purchase_id, destination, cancel, user_id, payment_status, card_last4 in purchases_data:
            obj, _ = Purchase.objects.update_or_create(
                purchase_id=purchase_id,
                defaults={
                    "destination": destination,
                    "cancel": cancel,
                    "user": accounts[user_id],
                    "payment_status": payment_status,
                    "card_last4": card_last4,
                },
            )
            purchases[purchase_id] = obj
        self.stdout.write(self.style.SUCCESS(f"注文: {len(purchases)}件"))

        # ====================================
        # 注文詳細 (shopping_purchasedetail)
        # ====================================
        if items:
            details_data = [
                # (purchase_detail_id, amount, item_id, purchase_id)
                (10001, 1, 200, 1001),
                (10002, 2, 201, 1002),
                (10003, 1, 202, 1003),
                (10004, 1, 220, 1004),
                (10005, 3, 250, 1005),
            ]
            valid_details = [(did, amt, iid, pid) for did, amt, iid, pid in details_data if iid in items]
            for detail_id, amount, item_id, purchase_id in valid_details:
                Purchasedetail.objects.update_or_create(
                    purchase_detail_id=detail_id,
                    defaults={"amount": amount, "item": items[item_id], "purchase": purchases[purchase_id]},
                )
            self.stdout.write(self.style.SUCCESS(f"注文詳細: {len(valid_details)}件"))
        else:
            self.stdout.write(self.style.WARNING("商品が未登録のため注文詳細はスキップしました"))

        # ====================================
        # 管理者 (administrator_admin)
        # ====================================
        admins_data = [
            ("admin001", "adminpass001"),
            ("admin002", "adminpass002"),
            ("admin003", "adminpass003"),
            ("admin004", "adminpass004"),
            ("admin005", "adminpass005"),
        ]
        for admin_id, raw_password in admins_data:
            Admin.objects.update_or_create(
                admin_id=admin_id,
                defaults={"password": make_password(raw_password)},
            )
        self.stdout.write(self.style.SUCCESS(f"管理者: {len(admins_data)}件"))

        # ====================================
        # 評価データ (shopping_review)
        # user001〜005 が全商品に5件ずつレビュー
        # おすすめ商品は高め（4〜5点）の評価
        # ====================================
        if items:
            Review.objects.all().delete()
            reviewers = list(accounts.values())
            reviews_to_create = []

            for item in Item.objects.all():
                for reviewer in reviewers:
                    if item.recommended:
                        # おすすめ商品：4〜5点を高確率で
                        rating = random.choices([5, 5, 4, 4, 3], k=1)[0]
                    else:
                        # 通常商品：2〜5点を幅広く
                        rating = random.choices([5, 4, 4, 3, 3, 2], k=1)[0]

                    title, comment = random.choice(self.REVIEW_TEMPLATES[rating])
                    reviews_to_create.append(Review(
                        rating=rating,
                        title=title,
                        comment=comment,
                        helpful_count=random.randint(0, 20),
                        is_verified_purchase=random.choice([True, False]),
                        item=item,
                        user=reviewer,
                    ))

            Review.objects.bulk_create(reviews_to_create)
            self.stdout.write(self.style.SUCCESS(f"評価データ: {len(reviews_to_create)}件（{Item.objects.count()}商品 × 5件）"))
        else:
            self.stdout.write(self.style.WARNING("商品が未登録のため評価データはスキップしました"))

        self.stdout.write(self.style.SUCCESS("=== サンプルデータの投入が完了しました ==="))
        self.stdout.write("")
        self.stdout.write("ログイン情報:")
        self.stdout.write("  会員: user001 / password001 〜 user005 / password005")
        self.stdout.write("  管理者: admin001 / adminpass001 〜 admin005 / adminpass005")