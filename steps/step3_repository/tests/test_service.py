"""Step 3: サービス層 (ShopService) のテスト.

ビジネスロジック (ShopService) をテストします。
リポジトリを注入 (DI) することで、グローバル状態に依存せず
完全に分離された環境でテストを実行できます。
"""

from typing import TYPE_CHECKING

import pytest
from domain.entity import Cart, CartItem

if TYPE_CHECKING:
    from domain.entity import Product
    from pytest_mock import MockerFixture
    from repository.cart_repository import CartRepository
    from repository.order_repository import OrderRepository
    from repository.product_repository import ProductRepository
    from service import ShopService


class TestGetProductsList:
    """商品一覧取得ロジックのテスト."""

    def test_returns_all_products(self, shop_service: ShopService) -> None:
        """全ての商品が返されること."""
        products = shop_service.get_products_list()
        assert len(products) == 3
        ids = [p.id for p in products]
        assert "P001" in ids
        assert "P002" in ids
        assert "P003" in ids


class TestAddToCart:
    """カート追加ロジックのテスト."""

    def test_adds_item_to_cart(
        self, shop_service: ShopService, cart_repo: CartRepository
    ) -> None:
        """商品がカートに追加されること."""
        shop_service.add_item_to_cart("user1", "P001", 2)
        cart = cart_repo.find_by_user_id("user1")
        assert cart is not None
        assert len(cart.items) == 1
        assert cart.items[0].product_id == "P001"
        assert cart.items[0].quantity == 2

    def test_increases_quantity_for_existing_item(
        self, shop_service: ShopService, cart_repo: CartRepository
    ) -> None:
        """同じ商品を追加すると数量が加算されること."""
        shop_service.add_item_to_cart("user1", "P001", 2)
        shop_service.add_item_to_cart("user1", "P001", 3)
        cart = cart_repo.find_by_user_id("user1")
        assert cart is not None
        assert len(cart.items) == 1
        assert cart.items[0].quantity == 5

    def test_rejects_nonexistent_product(
        self, shop_service: ShopService
    ) -> None:
        """存在しない商品IDの場合、ValueErrorがスローされること."""
        with pytest.raises(ValueError, match="見つかりません"):
            shop_service.add_item_to_cart("user1", "P999", 1)

    def test_rejects_insufficient_stock(
        self, shop_service: ShopService
    ) -> None:
        """在庫不足の場合、ValueErrorがスローされること."""
        with pytest.raises(ValueError, match="在庫が不足しています"):
            shop_service.add_item_to_cart("user1", "P002", 100)


class TestRemoveFromCart:
    """カート削除ロジックのテスト."""

    def test_removes_item_from_cart(
        self, shop_service: ShopService, cart_repo: CartRepository
    ) -> None:
        """カートから商品が削除されること."""
        shop_service.add_item_to_cart("user1", "P001", 1)
        shop_service.add_item_to_cart("user1", "P002", 2)
        shop_service.remove_item_from_cart("user1", "P001")
        cart = cart_repo.find_by_user_id("user1")
        assert cart is not None
        assert len(cart.items) == 1
        assert cart.items[0].product_id == "P002"

    def test_rejects_empty_cart(self, shop_service: ShopService) -> None:
        """空カートから削除しようとするとValueErrorがスローされること."""
        with pytest.raises(ValueError, match="カートが空です"):
            shop_service.remove_item_from_cart("user1", "P001")

    def test_rejects_nonexistent_item(self, shop_service: ShopService) -> None:
        """カートにない商品を削除しようとするとValueErrorがスローされること."""
        shop_service.add_item_to_cart("user1", "P001", 1)
        with pytest.raises(ValueError, match="カートにありません"):
            shop_service.remove_item_from_cart("user1", "P999")


class TestGetCartDetails:
    """カート詳細取得ロジックのテスト."""

    def test_calculates_totals_correctly(
        self, shop_service: ShopService
    ) -> None:
        """カート内容と金額(小計・消費税・合計)が正しく計算されること."""
        shop_service.add_item_to_cart("user1", "P001", 2)  # 2000 * 2 = 4000
        shop_service.add_item_to_cart("user1", "P003", 3)  # 500 * 3 = 1500

        details = shop_service.get_cart_details("user1")

        assert details is not None
        assert len(details.items) == 2
        assert details.subtotal == 5500
        assert details.tax == 550
        assert details.total == 6050

    def test_returns_none_for_empty_cart(
        self, shop_service: ShopService
    ) -> None:
        """空カートの場合は None が返されること."""
        details = shop_service.get_cart_details("user1")
        assert details is None

    def test_skips_invalid_product(
        self, shop_service: ShopService, cart_repo: CartRepository
    ) -> None:
        """カート内に存在しない商品が含まれていた場合スキップされること."""
        cart = Cart(
            user_id="user1",
            items=[CartItem(product_id="INVALID", quantity=1)],
        )
        cart_repo.save(cart)
        details = shop_service.get_cart_details("user1")
        assert details is not None
        assert details.subtotal == 0
        assert len(details.items) == 0


class TestPlaceOrder:
    """注文確定ロジックのテスト."""

    def test_creates_order_and_updates_stock(
        self,
        shop_service: ShopService,
        product_repo: ProductRepository,
        cart_repo: CartRepository,
        order_repo: OrderRepository,
    ) -> None:
        """注文作成・在庫減少・カートクリアが正しく行われること."""
        shop_service.add_item_to_cart("user1", "P001", 2)
        shop_service.add_item_to_cart("user1", "P002", 1)

        order = shop_service.place_order("user1")

        # 戻り値の検証
        assert order.user_id == "user1"
        assert order.subtotal == 5500
        assert order.tax == 550
        assert order.total == 6050
        assert "ORD-" in order.order_id

        # 副作用(データ更新)の検証
        assert order_repo.count() == 1
        p1 = product_repo.find_by_id("P001")
        assert p1 is not None
        assert p1.stock == 8
        p2 = product_repo.find_by_id("P002")
        assert p2 is not None
        assert p2.stock == 4
        cart = cart_repo.find_by_user_id("user1")
        assert cart is not None
        assert cart.is_empty

    def test_rejects_empty_cart(self, shop_service: ShopService) -> None:
        """カートが空の状態で注文しようとするとValueErrorが発生すること."""
        with pytest.raises(ValueError, match="カートが空です"):
            shop_service.place_order("user1")

    def test_rejects_order_with_insufficient_stock(
        self,
        shop_service: ShopService,
        product_repo: ProductRepository,
        cart_repo: CartRepository,
    ) -> None:
        """在庫不足時に注文が失敗し、副作用が発生しないこと."""
        shop_service.add_item_to_cart("user1", "P002", 3)

        # 別のプロセス等で在庫が減った想定
        product = product_repo.find_by_id("P002")
        assert product is not None
        product.stock = 1
        product_repo.save(product)

        with pytest.raises(ValueError, match="在庫が不足しています"):
            shop_service.place_order("user1")

        # カートや在庫がそのまま維持されることの確認
        p = product_repo.find_by_id("P002")
        assert p is not None
        assert p.stock == 1
        cart = cart_repo.find_by_user_id("user1")
        assert cart is not None
        assert cart.items[0].quantity == 3

    def test_rejects_order_with_invalid_product(
        self, shop_service: ShopService, cart_repo: CartRepository
    ) -> None:
        """存在しない商品がカートにある場合に注文が失敗すること."""
        cart = Cart(
            user_id="user1",
            items=[CartItem(product_id="INVALID", quantity=1)],
        )
        cart_repo.save(cart)
        with pytest.raises(ValueError, match="商品 INVALID が見つかりません"):
            shop_service.place_order("user1")

    def test_skips_product_disappeared_during_order(
        self,
        shop_service: ShopService,
        product_repo: ProductRepository,
        mocker: MockerFixture,
    ) -> None:
        """注文の検証後、計算処理の間に商品が削除された場合はスキップされること."""
        shop_service.add_item_to_cart("user1", "P001", 1)
        original_find = product_repo.find_by_id

        call_count = 0

        def mock_find_by_id(product_id: str) -> Product | None:
            nonlocal call_count
            call_count += 1
            # 1回目は在庫チェック用なので正常に返す
            # 2回目以降 (金額計算・在庫減少時) は None を返して
            # 削除されたことをシミュレート
            if call_count >= 2:
                return None
            return original_find(product_id)

        mocker.patch.object(
            product_repo, "find_by_id", side_effect=mock_find_by_id
        )
        order = shop_service.place_order("user1")

        # 商品がスキップされたため、アイテムは空で合計金額も0になる
        assert len(order.items) == 0
        assert order.total == 0


class TestGetOrderHistory:
    """注文履歴取得のテスト."""

    def test_returns_order_history(self, shop_service: ShopService) -> None:
        """注文履歴が返されること."""
        shop_service.add_item_to_cart("user1", "P001", 1)
        shop_service.place_order("user1")

        history = shop_service.get_order_history("user1")
        assert len(history) == 1
        assert history[0].total == 2200

    def test_returns_empty_list_when_no_orders(
        self, shop_service: ShopService
    ) -> None:
        """注文履歴がない場合は空リストが返されること."""
        history = shop_service.get_order_history("user1")
        assert history == []
