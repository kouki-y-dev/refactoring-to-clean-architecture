"""Domain layer tests for Step 7."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from domain.entity import (
    Cart,
    CartDetailItem,
    CartDetails,
    Order,
    OrderItem,
    Product,
)
from pydantic import ValidationError


class TestProduct:
    """Product エンティティのテスト."""

    def test_product_creation(self) -> None:
        """正常に商品を作成できる."""
        product = Product(id="P001", name="Tシャツ", price=2000, stock=10)
        assert product.id == "P001"
        assert product.name == "Tシャツ"
        assert product.price == 2000
        assert product.stock == 10

    def test_product_validation_negative_price(self) -> None:
        """負の価格はバリデーションエラー."""
        with pytest.raises(ValidationError):
            Product(id="P001", name="Tシャツ", price=-1000, stock=10)

    def test_product_validation_negative_stock(self) -> None:
        """負の在庫数はバリデーションエラー."""
        with pytest.raises(ValidationError):
            Product(id="P001", name="Tシャツ", price=2000, stock=-1)

    def test_has_enough_stock_true(self) -> None:
        """在庫が十分にある場合 True."""
        product = Product(id="P001", name="Tシャツ", price=2000, stock=10)
        assert product.has_enough_stock(10) is True
        assert product.has_enough_stock(5) is True

    def test_has_enough_stock_false(self) -> None:
        """在庫が不足している場合 False."""
        product = Product(id="P001", name="Tシャツ", price=2000, stock=10)
        assert product.has_enough_stock(11) is False

    def test_decrease_stock_success(self) -> None:
        """在庫減少が正常に行われる."""
        product = Product(id="P001", name="Tシャツ", price=2000, stock=10)
        product.decrease_stock(3)
        assert product.stock == 7

    def test_decrease_stock_insufficient(self) -> None:
        """在庫不足時に ValueError が発生する."""
        product = Product(id="P001", name="Tシャツ", price=2000, stock=10)
        with pytest.raises(
            ValueError, match="エラー: Tシャツ の在庫が不足しています"
        ):
            product.decrease_stock(11)


class TestCart:
    """Cart エンティティのテスト."""

    def test_cart_creation_empty(self) -> None:
        """空のカートが作成される."""
        cart = Cart(user_id="user1")
        assert cart.user_id == "user1"
        assert cart.items == []
        assert cart.is_empty is True

    def test_add_item_new(self) -> None:
        """新しい商品を追加できる."""
        cart = Cart(user_id="user1")
        cart.add_item("P001", 2)
        assert len(cart.items) == 1
        assert cart.items[0].product_id == "P001"
        assert cart.items[0].quantity == 2
        assert cart.is_empty is False

    def test_add_item_existing(self) -> None:
        """既存の商品の数量が加算される."""
        cart = Cart(user_id="user1")
        cart.add_item("P001", 2)
        cart.add_item("P001", 3)
        assert len(cart.items) == 1
        assert cart.items[0].product_id == "P001"
        assert cart.items[0].quantity == 5

    def test_remove_item_success(self) -> None:
        """商品をカートから削除できる."""
        cart = Cart(user_id="user1")
        cart.add_item("P001", 2)
        cart.add_item("P002", 1)
        cart.remove_item("P001")
        assert len(cart.items) == 1
        assert cart.items[0].product_id == "P002"

    def test_remove_item_not_found(self) -> None:
        """存在しない商品を削除しようとすると ValueError."""
        cart = Cart(user_id="user1")
        with pytest.raises(
            ValueError, match="エラー: 商品 P999 はカートにありません"
        ):
            cart.remove_item("P999")

    def test_clear_cart(self) -> None:
        """カートを空にできる."""
        cart = Cart(user_id="user1")
        cart.add_item("P001", 2)
        cart.clear()
        assert cart.is_empty is True
        assert len(cart.items) == 0


class TestCartDetails:
    """CartDetails 値オブジェクトのテスト."""

    def test_cart_details_creation(self) -> None:
        """CartDetails が正しく作成される."""
        item = CartDetailItem(
            product_id="P001",
            name="Tシャツ",
            price=2000,
            quantity=2,
            item_total=4000,
        )
        details = CartDetails(
            items=[item],
            subtotal=4000,
            tax=400,
            total=4400,
        )
        assert details.subtotal == 4000
        assert details.tax == 400
        assert details.total == 4400


class TestOrder:
    """Order エンティティのテスト."""

    def test_order_create_factory(self) -> None:
        """Create ファクトリメソッドで税金と合計が自動計算される."""
        items = [
            OrderItem(
                product_id="P001",
                name="Tシャツ",
                price=2000,
                quantity=1,
                subtotal=2000,
            ),
            OrderItem(
                product_id="P002",
                name="マグカップ",
                price=1200,
                quantity=2,
                subtotal=2400,
            ),
        ]
        now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
        order = Order.create(
            order_id="ord_001",
            user_id="user1",
            items=items,
            created_at=now,
        )
        assert order.order_id == "ord_001"
        assert order.user_id == "user1"
        assert order.subtotal == 4400
        assert order.tax == 440
        assert order.total == 4840
        assert order.created_at == now

    def test_order_create_default_datetime(self) -> None:
        """created_at を省略した場合は現在日時が自動設定される."""
        items = [
            OrderItem(
                product_id="P001",
                name="Tシャツ",
                price=2000,
                quantity=1,
                subtotal=2000,
            )
        ]
        order = Order.create(
            order_id="ord_001",
            user_id="user1",
            items=items,
        )
        assert order.created_at is not None
        assert order.total == 2200
