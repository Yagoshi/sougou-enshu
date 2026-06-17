# sougou-enshu

Djangoで構築したECサイトです。商品の閲覧・購入・決済・会員管理・AIチャットボットなどの機能を備えています。

---

## 機能一覧

### 会員向け
- 会員登録・ログイン・ログアウト・退会
- 会員情報の確認・更新
- 商品一覧・キーワード検索・カテゴリ絞り込み
- 商品詳細の閲覧
- カートへの追加・数量変更・削除
- クレジットカード決済（模擬決済API連携）
- 購入履歴の確認
- 商品レビューの投稿・閲覧（購入済み認証バッジ付き）
- AIチャットボットによる商品への質問（Gemini API連携）

### 管理者向け
- 管理者ログイン
- 商品の追加・編集・削除・画像アップロード
- おすすめ商品の設定
- 注文一覧の確認・キャンセル処理

---

## 技術スタック

| カテゴリ | 技術 |
|----------|------|
| バックエンド | Python 3.12 / Django 6.0 |
| データベース | MySQL 8.0 |
| フロントエンド | HTML / CSS（独自デザインシステム） |
| DB接続 | PyMySQL |
| 決済 | 模擬決済API（debt-trap） |
| 画像処理 | Pillow |
| AI チャットボット | Gemini API（google-generativeai） |

---

## ディレクトリ構成

```
sougou-enshu/
├── accounts/                   # 会員・管理者アプリ
│   ├── management/
│   │   └── commands/
│   │       └── seed.py         # サンプルデータ投入コマンド
│   ├── migrations/             # マイグレーションファイル
│   ├── templates/accounts/     # 会員・管理者画面テンプレート
│   ├── tests/                  # ユニットテスト
│   ├── models.py               # User・Adminモデル
│   ├── views.py                # 会員・管理者ビュー
│   ├── forms.py                # 会員フォーム
│   └── urls.py                 # 会員・管理者URL
├── store/                      # ECサイト本体アプリ
│   ├── migrations/             # マイグレーションファイル
│   ├── templates/store/        # 商品・カート・購入画面テンプレート
│   ├── tests/                  # ユニットテスト
│   ├── models.py               # Category・Item・Cart・Purchase・Reviewモデル
│   ├── views.py                # 商品・カート・購入・レビュー・チャットボットビュー
│   ├── forms.py                # 商品・レビューフォーム
│   └── urls.py                 # 商品・カートURL
├── shop01/                     # プロジェクト設定
│   ├── settings.py             # Django設定
│   ├── urls.py                 # ルーティング
│   ├── wsgi.py
│   └── __init__.py             # pymysql設定
├── media/                      # アップロード画像（Git管理対象外）
├── .env                        # 環境変数（Git管理対象外）
├── .env.example                # 環境変数のテンプレート
├── requirements.txt            # 必要パッケージ一覧
├── manage.py
├── チーム開発セットアップ手順.md
└── 動作確認手順書.md
```

---

## 環境構築手順

### 1. リポジトリをクローンする

```bash
git clone https://github.com/Yagoshi/sougou-enshu.git
cd sougou-enshu
git checkout develop
```

### 2. パッケージをインストールする

```bash
pip install -r requirements.txt
```

### 3. .envファイルを作成する

```bash
cp .env.example .env
```

VS Codeで `.env` を開いて以下の項目を自分の環境に合わせて編集してください。

```
DB_NAME=sougou-enshu        # 自分のDBの名前
DB_PASSWORD=P@ssw0rd        # 自分のMySQLパスワード
API_KEY=your-api-key-here   # 模擬決済APIのキー（後述）
GEMINI_API_KEY=your-gemini-api-key-here  # Gemini APIのキー（後述）
```

### 4. MySQLでデータベースを作成する

```bash
mysql -u root -p
```

```sql
CREATE DATABASE `sougou-enshu`;
exit;
```

### 5. マイグレーションを実行する

```bash
python manage.py migrate
```

### 6. サンプルデータを投入する

```bash
python manage.py seed --clear
```

### 7. 模擬決済APIのキーを取得する

1. ブラウザで http://15.152.44.182/ を開く
2. 「新規登録はこちら」からアカウントを作成する
3. ダッシュボードに表示されるAPIキーをコピーする
4. `.env` の `API_KEY=` に貼り付けて保存する

### 8. Gemini APIのキーを取得する

1. ブラウザで https://aistudio.google.com/ を開く
2. 「Get API key」→「Create API key」をクリックする
3. 表示されたAPIキーをコピーする
4. `.env` の `GEMINI_API_KEY=` に貼り付けて保存する

> ⚠️ Gemini APIキーは各自で取得してください。キーがない場合、商品詳細のチャットボットが動作しません。

### 9. 商品画像ファイルを取得する

商品画像は `media/` フォルダに保存されていますが、Gitの管理対象外のため別途共有が必要です。

**画像ファイルを受け取った場合（zipファイル）**

受け取った `media_items.zip` を `sougou-enshu/` フォルダに置いて解凍してください。

```bash
cd sougou-enshu
unzip media_items.zip
```

解凍後、`media/items/` フォルダに画像ファイルが入っていれば完了です。

> ⚠️ 画像ファイルがない場合でも動作はしますが、商品画像が表示されません。

**画像ファイルを共有する場合（配布する側）**

```bash
cd sougou-enshu
zip -r media_items.zip media/items/
```

作成した `media_items.zip` を班員に共有してください。

### 10. 開発サーバーを起動する

```bash
python manage.py runserver
```

ブラウザで http://127.0.0.1:8000 を開いてください。

---

## ログイン情報（サンプルデータ）

| 種別 | ID | パスワード |
|------|----|-----------| 
| 会員 | user001 〜 user005 | password001 〜 password005 |
| 管理者 | admin001 〜 admin005 | adminpass001 〜 adminpass005 |

管理者ログインURL: http://127.0.0.1:8000/admin_login

---

## ユニットテストの実行

```bash
# 全テスト実行
python manage.py test

# アプリ単位で実行
python manage.py test accounts
python manage.py test store
```

---

## ブランチ運用（GitFlow）

| ブランチ | 用途 |
|----------|------|
| `main` | リリース用。直接pushは禁止 |
| `develop` | 開発のベース。直接pushは禁止 |
| `feature/〇〇` | 機能追加の作業ブランチ |
| `bugfix/fix-〇〇` | バグ修正の作業ブランチ |

詳細は `チーム開発セットアップ手順.md` を参照してください。