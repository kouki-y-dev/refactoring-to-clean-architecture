"""Step 6: ユースケース層の単体テスト.

各ユースケース (ListProducts, AddToCart, RemoveFromCart,
ViewCart, PlaceOrder, GetOrderHistory)
の振る舞い・ビジネスロジックを検証します。
クリーンアーキテクチャに従い、ユースケースはドメイン層のリポジトリインターフェース
(IProductRepository 等) のみに依存するため、
テスト用具象クラスやモックを注入 (DI) して
外部環境に依存せずテストを実行できます。
"""

from typing import TYPE_CHECKING

import pytest
from domain.entity import Cart, CartItem

if TYPE_CHECKING:
    from domain.entity import Product
    from infrastructure.repository.cart_repository import (
        InMemoryCartRepository,
    )
    from infrastructure.repository.order_repository import (
        InMemoryOrderRepository,
    )
    from infrastructure.repository.product_repository import (
        InMemoryProductRepository,
    )
    from pytest_mock import MockerFixture
    from usecase.add_to_cart import AddToCartUseCase
    from usecase.get_order_history import GetOrderHistoryUseCase
    from usecase.list_products import ListProductsUseCase
    from usecase.place_order import PlaceOrderUseCase
    from usecase.remove_from_cart import RemoveFromCartUseCase
    from usecase.view_cart import ViewCartUseCase


class TestListProductsUseCase:
    """ListProductsUseCase のテスト."""

    def test_returns_all_products(
        self, list_products_usecase: ListProductsUseCase
    ) -> None:
        """全ての商品が返されること."""
        products = list_products_usecase.execute()
        assert len(products) == 3
        ids = [p.id for p in products]
        assert "P001" in ids
        assert "P002" in ids
        assert "P003" in ids


class TestAddToCartUseCase:
    """AddToCartUseCase のテスト."""

    def test_adds_item_to_cart_and_returns_product(
        self,
        add_to_cart_usecase: AddToCartUseCase,
        cart_repo: InMemoryCartRepository,
    ) -> None:
        """商品がカートに追加され、対象の Product が返されること."""
        product = add_to_cart_usecase.execute("user1", "P001", 2)
        assert product.id == "P001"
        assert product.name == "Tシャツ"

        cart = cart_repo.find_by_user_id("user1")
        assert cart is not None
        assert len(cart.items) == 1
        assert cart.items[0].product_id == "P001"
        assert cart.items[0].quantity == 2

    def test_increases_quantity_for_existing_item(
        self,
        add_to_cart_usecase: AddToCartUseCase,
        cart_repo: InMemoryCartRepository,
    ) -> None:
        """同じ商品を追加すると数量が加算されること."""
        add_to_cart_usecase.execute("user1", "P001", 2)
        add_to_cart_usecase.execute("user1", "P001", 3)
        cart = cart_repo.find_by_user_id("user1")
        assert cart is not None
        assert len(cart.items) == 1
        assert cart.items[0].quantity == 5

    def test_rejects_nonexistent_product(
        self, add_to_cart_usecase: AddToCartUseCase
    ) -> None:
        """存在しない商品IDの場合、ValueErrorがスローされること."""
        with pytest.raises(ValueError, match="見つかりません"):
            add_to_cart_usecase.execute("user1", "P999", 1)

    def test_rejects_insufficient_stock(
        self, add_to_cart_usecase: AddToCartUseCase
    ) -> None:
        """在庫不足の場合、ValueErrorがスローされること."""
        with pytest.raises(ValueError, match="在庫が不足しています"):
            add_to_cart_usecase.execute("user1", "P002", 100)


class TestRemoveFromCartUseCase:
    """RemoveFromCartUseCase のテスト."""

    def test_removes_item_from_cart(
        self,
        add_to_cart_usecase: AddToCartUseCase,
        remove_from_cart_usecase: RemoveFromCartUseCase,
        cart_repo: InMemoryCartRepository,
    ) -> None:
        """カートから商品が削除されること."""
        add_to_cart_usecase.execute("user1", "P001", 1)
        add_to_cart_usecase.execute("user1", "P002", 2)
        remove_from_cart_usecase.execute("user1", "P001")
        cart = cart_repo.find_by_user_id("user1")
        assert cart is not None
        assert len(cart.items) == 1
        assert cart.items[0].product_id == "P002"

    def test_rejects_empty_cart(
        self, remove_from_cart_usecase: RemoveFromCartUseCase
    ) -> None:
        """空カートから削除しようとするとValueErrorがスローされること."""
        with pytest.raises(ValueError, match="カートが空です"):
            remove_from_cart_usecase.execute("user1", "P001")

    def test_rejects_nonexistent_item(
        self,
        add_to_cart_usecase: AddToCartUseCase,
        remove_from_cart_usecase: RemoveFromCartUseCase,
    ) -> None:
        """カートにない商品を削除しようとするとValueErrorがスローされること."""
        add_to_cart_usecase.execute("user1", "P001", 1)
        with pytest.raises(ValueError, match="カートにありません"):
            remove_from_cart_usecase.execute("user1", "P999")


class TestViewCartUseCase:
    """ViewCartUseCase のテスト."""

    def test_calculates_totals_correctly(
        self,
        add_to_cart_usecase: AddToCartUseCase,
        view_cart_usecase: ViewCartUseCase,
    ) -> None:
        """カート内容と金額(小計・消費税・合計)が正しく計算されること."""
        add_to_cart_usecase.execute("user1", "P001", 2)  # 2000 * 2 = 4000
        add_to_cart_usecase.execute("user1", "P003", 3)  # 500 * 3 = 1500

        details = view_cart_usecase.execute("user1")

        assert details is not None
        assert len(details.items) == 2
        assert details.subtotal == 5500
        assert details.tax == 550
        assert details.total == 6050

    def test_returns_none_for_empty_cart(
        self, view_cart_usecase: ViewCartUseCase
    ) -> None:
        """空カートの場合は None が返されること."""
        details = view_cart_usecase.execute("user1")
        assert details is None

    def test_skips_invalid_product(
        self,
        view_cart_usecase: ViewCartUseCase,
        cart_repo: InMemoryCartRepository,
    ) -> None:
        """カート内に存在しない商品が含まれていた場合スキップされること."""
        cart = Cart(
            user_id="user1",
            items=[CartItem(product_id="INVALID", quantity=1)],
        )
        cart_repo.save(cart)
        details = view_cart_usecase.execute("user1")
        assert details is not None
        assert details.subtotal == 0
        assert len(details.items) == 0


class TestPlaceOrderUseCase:
    """PlaceOrderUseCase のテスト."""

    def test_creates_order_and_updates_stock(
        self,
        add_to_cart_usecase: AddToCartUseCase,
        place_order_usecase: PlaceOrderUseCase,
        product_repo: InMemoryProductRepository,
        cart_repo: InMemoryCartRepository,
        order_repo: InMemoryOrderRepository,
    ) -> None:
        """注文作成・在庫減少・カートクリアが正しく行われること."""
        add_to_cart_usecase.execute("user1", "P001", 2)
        add_to_cart_usecase.execute("user1", "P002", 1)

        order = place_order_usecase.execute("user1")

        # 戻り値の検証
        assert order.user_id == "user1"
        assert order.subtotal == 5200
        assert order.tax == 520
        assert order.total == 5720
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

    def test_rejects_empty_cart(
        self, place_order_usecase: PlaceOrderUseCase
    ) -> None:
        """カートが空の状態で注文しようとするとValueErrorが発生すること."""
        with pytest.raises(ValueError, match="カートが空です"):
            place_order_usecase.execute("user1")

    def test_rejects_order_with_insufficient_stock(
        self,
        add_to_cart_usecase: AddToCartUseCase,
        place_order_usecase: PlaceOrderUseCase,
        product_repo: InMemoryProductRepository,
        cart_repo: InMemoryCartRepository,
    ) -> None:
        """在庫不足時に注文が失敗し、副作用が発生しないこと."""
        add_to_cart_usecase.execute("user1", "P002", 3)

        # 在庫を強制的に減らす
        product = product_repo.find_by_id("P002")
        assert product is not None
        product.stock = 1
        product_repo.save(product)

        with pytest.raises(ValueError, match="在庫が不足しています"):
            place_order_usecase.execute("user1")

        # カートや在庫が維持されることの確認
        p = product_repo.find_by_id("P002")
        assert p is not None
        assert p.stock == 1
        cart = cart_repo.find_by_user_id("user1")
        assert cart is not None
        assert cart.items[0].quantity == 3

    def test_rejects_order_with_invalid_product(
        self,
        place_order_usecase: PlaceOrderUseCase,
        cart_repo: InMemoryCartRepository,
    ) -> None:
        """存在しない商品がカートにある場合に注文が失敗すること."""
        cart = Cart(
            user_id="user1",
            items=[CartItem(product_id="INVALID", quantity=1)],
        )
        cart_repo.save(cart)
        with pytest.raises(ValueError, match="商品 INVALID が見つかりません"):
            place_order_usecase.execute("user1")

    def test_skips_product_disappeared_during_order(
        self,
        add_to_cart_usecase: AddToCartUseCase,
        place_order_usecase: PlaceOrderUseCase,
        product_repo: InMemoryProductRepository,
        mocker: MockerFixture,
    ) -> None:
        """注文の検証後、計算処理の間に商品が削除された場合はスキップされること."""
        add_to_cart_usecase.execute("user1", "P001", 1)
        original_find = product_repo.find_by_id

        call_count = 0

        def mock_find_by_id(product_id: str) -> Product | None:
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                return None
            return original_find(product_id)

        mocker.patch.object(
            product_repo, "find_by_id", side_effect=mock_find_by_id
        )
        order = place_order_usecase.execute("user1")

        assert len(order.items) == 0
        assert order.total == 0


class TestGetOrderHistoryUseCase:
    """GetOrderHistoryUseCase のテスト."""

    def test_returns_order_history(
        self,
        add_to_cart_usecase: AddToCartUseCase,
        place_order_usecase: PlaceOrderUseCase,
        get_order_history_usecase: GetOrderHistoryUseCase,
    ) -> None:
        """注文履歴が返されること."""
        add_to_cart_usecase.execute("user1", "P001", 1)
        place_order_usecase.execute("user1")

        history = get_order_history_usecase.execute("user1")
        assert len(history) == 1
        assert history[0].total == 2200

    def test_returns_empty_list_when_no_orders(
        self, get_order_history_usecase: GetOrderHistoryUseCase
    ) -> None:
        """注文履歴がない場合は空リストが返されること."""
        history = get_order_history_usecase.execute("user1")
        assert history == []
