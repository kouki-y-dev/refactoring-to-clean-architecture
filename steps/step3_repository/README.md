# Step 3: Repository パターンの導入 (Repository Pattern)

## 概要

Step 2 ではドメインモデル（エンティティ・値オブジェクト）を導入し、ビジネスルールをカプセル化しました。しかし、データの保存・取得は依然として単一の `data_access.py` 内のグローバル辞書を操作する手続き的な関数群に依存しており、`service.py` も具象モジュールに直接依存していました。

Step 3 では、データアクセスの詳細（辞書操作や将来的な DB 操作）を隠蔽し、ドメインモデル（集約）の永続化と再構築をコレクションのように扱う **Repository パターン** を導入しました。また、サービス層に対してリポジトリインスタンスを**コンストラクタ注入（Dependency Injection: DI）**することで、グローバル状態への依存を排除しました。

```
steps/step3_repository/
├── src/
│   ├── domain/
│   │   ├── __init__.py
│   │   └── entity.py              # ドメインモデル（Product, Cart, Order 等）
│   ├── repository/                # 【NEW】リポジトリ層（データ永続化のカプセル化）
│   │   ├── __init__.py
│   │   ├── cart_repository.py     # カートリポジトリ（CartRepository）
│   │   ├── order_repository.py    # 注文リポジトリ（OrderRepository）
│   │   └── product_repository.py  # 商品リポジトリ（ProductRepository）
│   ├── cli.py                     # プレゼンテーション層（CLI クラス）
│   ├── main.py                    # エントリーポイント（Composition Root / DI）
│   └── service.py                 # サービス層（ShopService クラス）
└── tests/
    ├── conftest.py                # テスト用フィクスチャ（リポジトリ・サービスの生成）
    ├── test_cli.py                # CLI のテスト
    ├── test_domain.py             # ドメインモデル単体テスト
    ├── test_repository.py         # 【NEW】リポジトリ層単体テスト
    └── test_service.py            # サービス層のテスト
```

---

## 実行方法 (How to Run)

### アプリケーションの実行 (CLI)

```bash
uv run steps/step3_repository/src/main.py
```

### テストの実行

```bash
# Step 3 のテストのみを実行
uv run poe test-step3
```

---

## 構成とコードの解説

### 1. `src/repository/` (リポジトリ層) 【NEW】
データアクセスの手続き的関数群（`data_access.py`）を廃止し、ドメインモデル（集約）ごとに特化したリポジトリクラスを実装しました。

- **`ProductRepository` (`product_repository.py`)**:
  - 商品エンティティ（`Product`）のコレクションとして振る舞います。
  - `find_all() -> list[Product]`: 全商品の取得。
  - `find_by_id(product_id: str) -> Product | None`: 商品IDによる検索。
  - `save(product: Product) -> None`: 商品の追加・更新。
- **`CartRepository` (`cart_repository.py`)**:
  - ユーザーごとのカートエンティティ（`Cart`）の永続化を担当します。
  - `find_by_user_id(user_id: str) -> Cart | None`: カートの取得。
  - `get_or_create(user_id: str) -> Cart`: 既存カートの取得、存在しなければ新規作成。
  - `save(cart: Cart) -> None`: カートの保存。
  - `delete(user_id: str) -> None`: カートの削除。
- **`OrderRepository` (`order_repository.py`)**:
  - 確定した注文エンティティ（`Order`）の保存と履歴検索を担当します。
  - `save(order: Order) -> None`: 注文の保存。
  - `find_by_id(order_id: str) -> Order | None`: 注文IDによる検索。
  - `find_by_user_id(user_id: str) -> list[Order]`: ユーザー別の注文履歴取得。
  - `next_order_id() -> str`: 注文ID（`ORD-0001` 等）の採番。

### 2. `src/service.py` (サービス層)
従来のモジュールレベルの関数群から、各リポジトリを保持する **`ShopService` クラス** へリファクタリングしました。
- コンストラクタでリポジトリを受け取る（**Constructor Injection**）:
  ```python
  class ShopService:
      def __init__(
          self,
          product_repo: ProductRepository,
          cart_repo: CartRepository,
          order_repo: OrderRepository,
      ) -> None:
          self.product_repo = product_repo
          self.cart_repo = cart_repo
          self.order_repo = order_repo
  ```
- リポジトリからエンティティを取得し、ドメインエンティティのメソッド（`cart.add_item()`, `product.decrease_stock()` 等）を実行後、リポジトリに保存（`cart_repo.save(cart)`）するという、ドメイン駆動の自然なフローを実現しています。

### 3. `src/cli.py` & `src/main.py` (プレゼンテーション層 & エントリーポイント)
- **`cli.py`**: `CLI` クラスとして定義し、コンストラクタで `ShopService` を受け取ります。
- **`main.py` (Composition Root)**:
  - アプリケーション起動時にリポジトリを生成し、サービスへ注入、さらにそれを CLI へ注入して起動します。

---

## 前回 (Step 2) からの改善点

1. **データアクセスとドメイン操作の明確な分離**
   - Step 2 の `data_access.add_to_cart()` のように「データアクセス層の中でドメイン操作を行う」という責務の曖昧さが解消されました。
   - リポジトリは「保管庫（コレクション）」に徹し、ビジネスルールはドメインエンティティが実行し、サービス層がその一連の流れを調整します。
2. **グローバル変数の完全排除**
   - `data_access.py` で保持していたモジュールレベルのグローバル辞書（`products`, `carts`, `orders`）を全廃しました。
   - 各リポジトリのインスタンス内部で状態をカプセル化して保持します。
3. **テスト容易性（Testability）と独立性の向上**
   - グローバル変数がなくなったため、テストごとに `conftest.py` でグローバル辞書をリセット（初期化）する必要がなくなりました。
   - 各テストは `pytest.fixture` で生成された独立したリポジトリインスタンス・サービスインスタンスを利用でき、テスト間の状態汚染が完全に防止されます。

---

## 現時点での問題点

Repository パターンを導入したことでデータアクセスが綺麗に整理されましたが、クリーンアーキテクチャの観点からは以下の課題が残っています。

1. **サービス層の肥大化と多責務（Single Responsibility Principle の課題）**
   - 1つの `ShopService` クラスに「商品一覧」「カート操作」「注文確定」「履歴参照」の全ユースケースが詰め込まれています。
   - 機能が増えるにつれて `ShopService` が巨大化し、変更理由が複数存在する状態になります。
   - ⇒ **Step 4 (UseCase 層の導入)** で単一責務のユースケースクラスに分割します。
2. **具象リポジトリへの直接依存（Dependency Inversion Principle: DIP 違反）**
   - `ShopService` は `ProductRepository` などの「具象クラス」に直接依存しています。
   - 将来的に SQLite や PostgreSQL、外部 API などの異なる永続化手段に差し替える際、サービス層の型定義や実装が影響を受ける可能性があります。
   - リポジトリの抽象（Interface / Protocol）をドメイン層/ユースケース層に定義し、インフラ層がそれを実装するという「依存関係の逆転」がまだ行われていません。
   - ⇒ **Step 5 (依存関係逆転の原則 DIP の適用)** で解決します。

---

## 次に導入するもの (Step 4: ユースケース層の導入)

次の **Step 4: UseCase** では、アプリケーションの利用シナリオ（ユースケース）ごとにクラスを分離します。

- **単一責任のユースケース**:
  - `ListProductsUseCase`, `AddToCartUseCase`, `ViewCartUseCase`, `PlaceOrderUseCase`, `GetOrderHistoryUseCase` などの独立したクラスを作成します。
- **入力・出力の明確化 (DTO / Request & Response)**:
  - プレゼンテーション層とユースケース層の間で受け渡すデータ構造を明確にし、UI の都合とビジネスロジックをさらに疎結合にします。
