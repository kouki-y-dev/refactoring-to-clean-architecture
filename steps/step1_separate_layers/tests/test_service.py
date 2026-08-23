"""Step 1: 関心の分離 (Service Layer) のテスト.

ビジネスロジック (service.py) を直接テストします。
UI (print) から分離されたため、戻り値や例外の送出を
使ってロジックのみをシンプルにテストできるようになりました。
ただし、データアクセスはまだグローバル変数に依存しているため、
フィクスチャによる状態のリセットは引き続き必要です。
"""

import data_access  # ty: ignore[unresolved-import]
import pytest
import service  # ty: ignore[unresolved-import]


class TestGetProductsList:
    """商品一覧取得ロジックのテスト."""

    def test_returns_all_products(self) -> None:
        """全ての商品が返されること."""
        products = service.get_products_list()
        assert len(products) == 3
        assert "P001" in products
        assert products["P001"]["name"] == "Tシャツ"


class TestAddToCart:
    """カート追加ロジックのテスト."""

    def test_adds_item_to_cart(self) -> None:
        """商品がカートに追加されること."""
        service.add_item_to_cart("user1", "P001", 2)
        cart = data_access.get_cart("user1")
        assert len(cart) == 1
        assert cart[0]["product_id"] == "P001"
        assert cart[0]["quantity"] == 2

    def test_increases_quantity_for_existing_item(self) -> None:
        """同じ商品を追加すると数量が加算されること."""
        service.add_item_to_cart("user1", "P001", 2)
        service.add_item_to_cart("user1", "P001", 3)
        cart = data_access.get_cart("user1")
        assert len(cart) == 1
        assert cart[0]["quantity"] == 5

    def test_rejects_nonexistent_product(self) -> None:
        """存在しない商品IDの場合、ValueErrorがスローされること."""
        with pytest.raises(ValueError, match="見つかりません"):
            service.add_item_to_cart("user1", "P999", 1)

    def test_rejects_insufficient_stock(self) -> None:
        """在庫不足の場合、ValueErrorがスローされること."""
        with pytest.raises(ValueError, match="在庫が不足しています"):
            service.add_item_to_cart("user1", "P002", 100)


class TestRemoveFromCart:
    """カート削除ロジックのテスト."""

    def test_removes_item_from_cart(self) -> None:
        """カートから商品が削除されること."""
        service.add_item_to_cart("user1", "P001", 1)
        service.add_item_to_cart("user1", "P002", 2)
        service.remove_item_from_cart("user1", "P001")
        cart = data_access.get_cart("user1")
        assert len(cart) == 1
        assert cart[0]["product_id"] == "P002"

    def test_rejects_empty_cart(self) -> None:
        """空カートから削除しようとするとValueErrorがスローされること."""
        with pytest.raises(ValueError, match="カートが空です"):
            service.remove_item_from_cart("user1", "P001")

    def test_rejects_nonexistent_item(self) -> None:
        """カートにない商品を削除しようとするとValueErrorがスローされること."""
        service.add_item_to_cart("user1", "P001", 1)
        with pytest.raises(ValueError, match="カートにありません"):
            service.remove_item_from_cart("user1", "P999")


class TestGetCartDetails:
    """カート詳細取得ロジックのテスト."""

    def test_calculates_totals_correctly(self) -> None:
        """カート内容と金額(小計・消費税・合計)が正しく計算されること."""
        service.add_item_to_cart("user1", "P001", 2)  # 2000 * 2 = 4000
        service.add_item_to_cart("user1", "P003", 3)  # 500 * 3 = 1500

        details = service.get_cart_details("user1")

        assert len(details["items"]) == 2
        assert details["subtotal"] == 5500
        assert details["tax"] == 550
        assert details["total"] == 6050

    def test_returns_empty_dict_for_empty_cart(self) -> None:
        """空カートの場合は空の辞書が返されること."""
        details = service.get_cart_details("user1")
        assert details == {}


class TestPlaceOrder:
    """注文確定ロジックのテスト."""

    def test_creates_order_and_updates_stock(self) -> None:
        """注文作成・在庫減少・カートクリアが正しく行われること."""
        service.add_item_to_cart("user1", "P001", 2)
        service.add_item_to_cart("user1", "P002", 1)

        order = service.place_order("user1")

        # 戻り値の検証
        assert order["user_id"] == "user1"
        assert order["subtotal"] == 5500
        assert order["tax"] == 550
        assert order["total"] == 6050
        assert "ORD-" in order["order_id"]

        # 副作用(データ更新)の検証
        orders = data_access.get_all_orders()
        assert len(orders) == 1
        assert data_access.get_product("P001")["stock"] == 8
        assert data_access.get_product("P002")["stock"] == 4
        assert data_access.get_cart("user1") == []

    def test_rejects_order_with_insufficient_stock(self) -> None:
        """在庫不足時に注文が失敗し、副作用が発生しないこと."""
        service.add_item_to_cart("user1", "P002", 3)
        # 別のプロセス等で在庫が減った想定
        data_access.update_product_stock("P002", 4)  # 残り1になる

        with pytest.raises(ValueError, match="在庫が不足しています"):
            service.place_order("user1")

        # 注文は作成されない
        assert len(data_access.get_all_orders()) == 0
        # カートは維持される
        assert len(data_access.get_cart("user1")) == 1


class TestGetOrderHistory:
    """注文履歴取得のテスト."""

    def test_returns_order_history(self) -> None:
        """注文履歴が返されること."""
        service.add_item_to_cart("user1", "P001", 1)
        service.place_order("user1")

        history = service.get_order_history("user1")
        assert len(history) == 1
        assert history[0]["total"] == 2200

    def test_returns_empty_list_when_no_orders(self) -> None:
        """注文履歴がない場合は空リストが返されること."""
        history = service.get_order_history("user1")
        assert history == []
