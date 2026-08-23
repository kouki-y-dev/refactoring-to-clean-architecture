"""Step 0: Monolith のテスト.

このテストでは、モノリシックなコードをテストする際の
「つらさ」を体感する。

つらいポイント:
  1. グローバル状態のリセット:
     各テストの前に products / carts / orders を
     手動でリセットする必要がある。
     リセットを忘れると、前のテストの状態が残って
     テストが壊れる。

  2. print() のキャプチャ:
     関数が値を返さず print() するため、
     出力の検証には capsys フィクスチャが必要。
     「何が返ったか」ではなく
     「何が印刷されたか」をテストすることになる。

  3. 部分的なテストが困難:
     ビジネスロジックだけをテストしたくても、
     print() やグローバル状態への副作用と切り離せない
     ため、常に統合テストのようになる。
"""

import main
import pytest


@pytest.fixture(autouse=True)
def _reset_global_state() -> None:
    """グローバル状態を初期値にリセットする.

    つらいポイント:
    テストごとにこのフィクスチャで状態をリセットしないと
    テスト間で状態が共有されてしまう。
    しかもリセット漏れがあっても実行時エラーにならず、
    テストが不安定になる。
    """
    main.products.clear()
    main.products.update(
        {
            "P001": {
                "name": "Tシャツ",
                "price": 2000,
                "stock": 10,
            },
            "P002": {
                "name": "マグカップ",
                "price": 1500,
                "stock": 5,
            },
            "P003": {
                "name": "ステッカー",
                "price": 500,
                "stock": 20,
            },
        }
    )
    main.carts.clear()
    main.orders.clear()


# ===================================================================
# 商品一覧のテスト
# ===================================================================


class TestListProducts:
    """商品一覧のテスト."""

    def test_displays_all_products(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """全商品が表示されること.

        つらいポイント:
        list_products() は値を返さないので、
        capsys で stdout をキャプチャして
        文字列マッチで検証するしかない。
        出力フォーマットが変わるとテストが壊れる。
        """
        main.list_products()
        captured = capsys.readouterr()
        assert "Tシャツ" in captured.out
        assert "マグカップ" in captured.out
        assert "ステッカー" in captured.out
        assert "¥2000" in captured.out
        assert "¥1500" in captured.out
        assert "¥500" in captured.out


# ===================================================================
# カート操作のテスト
# ===================================================================


class TestAddToCart:
    """カート追加のテスト."""

    def test_adds_item_to_cart(self) -> None:
        """商品がカートに追加されること.

        つらいポイント:
        テストの検証がグローバル変数 main.carts を
        直接参照している。
        内部のデータ構造 (dict のキー名など) を
        知っている必要がある。
        """
        main.add_to_cart("user1", "P001", 2)
        assert len(main.carts["user1"]) == 1
        assert main.carts["user1"][0]["product_id"] == "P001"
        assert main.carts["user1"][0]["quantity"] == 2

    def test_increases_quantity_for_existing_item(
        self,
    ) -> None:
        """同じ商品を追加すると数量が加算されること."""
        main.add_to_cart("user1", "P001", 2)
        main.add_to_cart("user1", "P001", 3)
        assert len(main.carts["user1"]) == 1
        assert main.carts["user1"][0]["quantity"] == 5

    def test_rejects_nonexistent_product(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """存在しない商品IDでエラーが出力されること."""
        main.add_to_cart("user1", "P999", 1)
        captured = capsys.readouterr()
        assert "エラー" in captured.out
        assert "P999" in captured.out
        assert "user1" not in main.carts

    def test_rejects_insufficient_stock(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """在庫超過でエラーが出力されること."""
        main.add_to_cart("user1", "P002", 100)
        captured = capsys.readouterr()
        assert "エラー" in captured.out
        assert "在庫が不足" in captured.out
        assert "user1" not in main.carts


# ===================================================================
# カート削除のテスト
# ===================================================================


class TestRemoveFromCart:
    """カート削除のテスト."""

    def test_removes_item_from_cart(self) -> None:
        """カートから商品が削除されること."""
        main.add_to_cart("user1", "P001", 1)
        main.add_to_cart("user1", "P002", 2)
        main.remove_from_cart("user1", "P001")
        assert len(main.carts["user1"]) == 1
        assert main.carts["user1"][0]["product_id"] == "P002"

    def test_rejects_empty_cart(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """空カートから削除でエラーが出力されること."""
        main.remove_from_cart("user1", "P001")
        captured = capsys.readouterr()
        assert "エラー" in captured.out

    def test_rejects_nonexistent_item(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """カートにない商品の削除でエラーが出力."""
        main.add_to_cart("user1", "P001", 1)
        main.remove_from_cart("user1", "P999")
        captured = capsys.readouterr()
        assert "エラー" in captured.out
        assert "P999" in captured.out


# ===================================================================
# カート表示のテスト
# ===================================================================


class TestViewCart:
    """カート表示のテスト."""

    def test_displays_cart_with_totals(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """カート内容と金額が正しく表示されること.

        つらいポイント:
        金額の計算ロジックを検証したいだけなのに、
        print 出力をパースして文字列マッチで検証している。
        ロジックのテストとは言い難い。
        """
        main.add_to_cart("user1", "P001", 2)  # 4000
        main.add_to_cart("user1", "P003", 3)  # 1500
        # 小計: 5500, 消費税: 550, 合計: 6050

        # capsys をリセットしてから view_cart を呼ぶ
        capsys.readouterr()
        main.view_cart("user1")
        captured = capsys.readouterr()

        assert "¥4000" in captured.out
        assert "¥1500" in captured.out
        assert "小計: ¥5500" in captured.out
        assert "消費税: ¥550" in captured.out
        assert "合計: ¥6050" in captured.out

    def test_displays_empty_cart_message(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """空カートでメッセージが表示されること."""
        main.view_cart("user1")
        captured = capsys.readouterr()
        assert "カートは空です" in captured.out


# ===================================================================
# 注文確定のテスト
# ===================================================================


class TestPlaceOrder:
    """注文確定のテスト."""

    def test_creates_order_and_updates_stock(self) -> None:
        """注文作成・在庫減少・カートクリアされること.

        つらいポイント:
        1つのテストで3つの副作用を検証している。
        どれか1つが壊れても原因の特定が難しい。
        """
        main.add_to_cart("user1", "P001", 2)
        main.add_to_cart("user1", "P002", 1)
        main.place_order("user1")

        # 注文が作成されている
        assert len(main.orders) == 1
        order = next(iter(main.orders.values()))
        assert order["user_id"] == "user1"
        # subtotal=5500, tax=550, total=6050
        assert order["subtotal"] == 5500
        assert order["tax"] == 550
        assert order["total"] == 6050

        # 在庫が減少している
        assert main.products["P001"]["stock"] == 8
        assert main.products["P002"]["stock"] == 4

        # カートがクリアされている
        assert main.carts["user1"] == []

    def test_rejects_order_with_insufficient_stock(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """在庫不足時に注文が失敗すること."""
        main.add_to_cart("user1", "P002", 3)
        # 在庫を手動で減らす -- 別ユーザーが購入した想定
        main.products["P002"]["stock"] = 1

        capsys.readouterr()
        main.place_order("user1")
        captured = capsys.readouterr()

        assert "エラー" in captured.out
        assert "在庫が不足" in captured.out
        # 注文が作成されていない
        assert len(main.orders) == 0
        # 在庫は変わらない
        assert main.products["P002"]["stock"] == 1

    def test_rejects_order_with_empty_cart(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """空カートで注文するとエラーになること."""
        main.place_order("user1")
        captured = capsys.readouterr()
        assert "エラー" in captured.out
        assert "カートが空" in captured.out


# ===================================================================
# 注文履歴のテスト
# ===================================================================


class TestViewOrderHistory:
    """注文履歴のテスト."""

    def test_displays_order_history(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """注文後に履歴が参照できること."""
        main.add_to_cart("user1", "P001", 1)
        main.place_order("user1")

        capsys.readouterr()
        main.view_order_history("user1")
        captured = capsys.readouterr()

        assert "ORD-0001" in captured.out
        assert "Tシャツ" in captured.out

    def test_displays_empty_history_message(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """注文がない場合にメッセージが表示されること."""
        main.view_order_history("user1")
        captured = capsys.readouterr()
        assert "注文履歴はありません" in captured.out
