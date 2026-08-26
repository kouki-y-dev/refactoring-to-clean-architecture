# Step 4: ユースケース層の導入 (Use Case Layer)

## 概要

Step 3 では Repository パターンを導入し、データアクセスのカプセル化と DI を実現しました。しかし、すべてのビジネスロジックが単一の `ShopService` クラスに集約されており、複数の責務を抱える「神クラス（God Class）」になっていました。また、プレゼンテーション層（CLI）が商品名を取得するためにリポジトリを直接参照するなどの責務の漏れ出しも存在していました。

Step 4 では、アプリケーションの利用シナリオ（ユースケース）ごとにクラスを分離した **ユースケース層 (`src/usecase/`)** を導入しました。各ユースケースクラスは単一責任の原則（SRP）に従い、必要なリポジトリのみを受け取ってビジネスロジックを実行します。

```
steps/step4_usecase/
├── README.md
├── src/
│   ├── domain/
│   │   ├── __init__.py
│   │   └── entity.py              # ドメインモデル（Product, Cart, Order 等）
│   ├── repository/                # リポジトリ層（データ永続化のカプセル化）
│   │   ├── __init__.py
│   │   ├── cart_repository.py     # カートリポジトリ（CartRepository）
│   │   ├── order_repository.py    # 注文リポジトリ（OrderRepository）
│   │   └── product_repository.py  # 商品リポジトリ（ProductRepository）
│   ├── usecase/                   # 【NEW】ユースケース層（利用シナリオごとの分割）
│   │   ├── __init__.py
│   │   ├── add_to_cart.py         # カート追加（AddToCartUseCase）
│   │   ├── get_order_history.py   # 注文履歴参照（GetOrderHistoryUseCase）
│   │   ├── list_products.py       # 商品一覧取得（ListProductsUseCase）
│   │   ├── place_order.py         # 注文確定（PlaceOrderUseCase）
│   │   ├── remove_from_cart.py    # カート削除（RemoveFromCartUseCase）
│   │   └── view_cart.py           # カート表示・集計（ViewCartUseCase）
│   ├── cli.py                     # プレゼンテーション層（CLI クラス）
│   └── main.py                    # エントリーポイント（Composition Root / DI）
└── tests/
    ├── conftest.py                # テスト用フィクスチャ（リポジトリ・ユースケース・CLI の生成）
    ├── test_cli.py                # CLI のテスト
    ├── test_domain.py             # ドメインモデル単体テスト
    ├── test_repository.py         # リポジトリ層単体テスト
    └── test_usecase.py            # 【NEW】ユースケース層単体テスト
```

---

## 実行方法 (How to Run)

### アプリケーションの実行 (CLI)

```bash
uv run steps/step4_usecase/src/main.py
```

### テストの実行

```bash
# Step 4 のテストのみを実行
uv run poe test-step4
```

---

## 構成とコードの解説

### 1. `src/usecase/` (ユースケース層) 【NEW】

単一の肥大化した `ShopService` を廃止し、利用シナリオごとに独立したユースケースクラスを作成しました。メソッド名は `execute(...)` に統一しています。

- **`ListProductsUseCase` (`list_products.py`)**:
  - 商品一覧を取得します。
  - 依存: `ProductRepository`
- **`AddToCartUseCase` (`add_to_cart.py`)**:
  - 在庫チェックを行い、カートに商品を追加・更新します。
  - 戻り値として追加された `Product` を返すことで、呼び出し元（CLI）がリポジトリを直接参照する必要をなくしています。
  - 依存: `ProductRepository`, `CartRepository`
- **`RemoveFromCartUseCase` (`remove_from_cart.py`)**:
  - カートから指定された商品を削除します。
  - 依存: `CartRepository`
- **`ViewCartUseCase` (`view_cart.py`)**:
  - カート内の商品詳細・小計・消費税・合計金額（`CartDetails`）を集計して返します。
  - 依存: `CartRepository`, `ProductRepository`
- **`PlaceOrderUseCase` (`place_order.py`)**:
  - 在庫チェック → 注文エンティティ作成 → 注文保存 → 在庫減少・保存 → カートクリアという一連の注文確定処理を実行します。
  - 依存: `CartRepository`, `ProductRepository`, `OrderRepository`
- **`GetOrderHistoryUseCase` (`get_order_history.py`)**:
  - ユーザーの注文履歴を取得します。
  - 依存: `OrderRepository`

### 2. `src/cli.py` (プレゼンテーション層)

- `CLI` クラスは `ShopService` ではなく、各ユースケースクラスをコンストラクタで受け取る形に変更されました。
- UI 側で必要な商品名表示なども `AddToCartUseCase.execute()` の戻り値から直接取得できるため、**プレゼンテーション層からリポジトリへの直接参照が完全に排除** されました。

### 3. `src/main.py` (Composition Root)

- アプリケーション起動時にリポジトリを生成し、各ユースケースに必要なリポジトリを注入（Constructor Injection）し、それらを CLI に注入して起動します。

```python
# リポジトリの初期化
product_repo = ProductRepository()
cart_repo = CartRepository()
order_repo = OrderRepository()

# ユースケースの初期化 (必要なリポジトリのみを注入)
list_products_usecase = ListProductsUseCase(product_repo=product_repo)
add_to_cart_usecase = AddToCartUseCase(
    product_repo=product_repo, cart_repo=cart_repo
)
...

# CLI の初期化
cli = CLI(...)
cli.main_menu()
```

---

## 前回 (Step 3) からの改善点

1. **単一責任の原則 (Single Responsibility Principle: SRP) の徹底**
   - 1つの `ShopService` クラスに全機能が詰め込まれていた状態を解消しました。
   - 「カート追加のロジックを変更したい」場合は `AddToCartUseCase` だけを、「注文確定のフローを変更したい」場合は `PlaceOrderUseCase` だけを変更すればよくなり、変更の影響範囲が明確になりました。
2. **依存関係の最小化 (Interface Segregation 的アプローチ)**
   - 各ユースケースは自身が必要とするリポジトリのみに依存します（例: `RemoveFromCartUseCase` は `CartRepository` のみ、`GetOrderHistoryUseCase` は `OrderRepository` のみ）。
   - 不要なリポジトリへの不要な結合が排除されました。
3. **プレゼンテーション層の純粋化**
   - CLI がリポジトリの内部状態（`service.product_repo` など）を直接覗き見るアンチパターンが解消され、ユースケースを呼び出すだけのクリーンなインターフェースになりました。

---

## 現時点での問題点

ユースケース層の導入によってアプリケーションロジックの整理が進みましたが、クリーンアーキテクチャの観点からは以下の課題が残っています。

1. **具象リポジトリへの直接依存（Dependency Inversion Principle: DIP 違反）**
   - 各ユースケースクラスは依然として `ProductRepository` などの「具象クラス」に直接依存しています。
   - 例えば、将来的にデータベース（SQLite, PostgreSQL）や外部 API 連携のリポジトリへ移行する際、ユースケース層の型アノテーションやインポートを書き換える必要があります。
   - 本来、ユースケース層（内側の層）はリポジトリのインターフェース（抽象）のみを知るべきであり、リポジトリ層（外側の層）がそのインターフェースを実装する形にする必要があります。
   - ⇒ **Step 5 (依存関係逆転の原則 DIP の適用)** で解決します。

---

## 次に導入するもの (Step 5: 依存関係逆転の原則 DIP の適用)

次の **Step 5: Dependency Inversion** では、Python の `abc.ABC` を用いてリポジトリのインターフェースを定義します。

- **リポジトリインターフェースの抽出**:
  - `IProductRepository`, `ICartRepository`, `IOrderRepository`
- **依存関係の逆転**:
  - ユースケース層は抽象インターフェースに依存し、具象リポジトリクラスがそのインターフェースを満たすように実装します。
