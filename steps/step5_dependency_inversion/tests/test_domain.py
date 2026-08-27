"""Step 5: ドメインモデル単体テスト.

Pydantic ドメインモデル (entity.py) のバリデーション、
ドメインメソッド、ファクトリ、イミュータビリティを検証します。
リポジトリ層やユースケース層には依存しません。
"""

from datetime import UTC, datetime

import pytest
from domain.entity import (
    Cart,
    CartDetailItem,
    CartDetails,
    CartItem,
    Order,
    OrderItem,
    Product,
)
from pydantic import ValidationError

# ===================================================================
# Product
# ===================================================================


class TestProduct:
    """Product エンティティのテスト."""

    def test_creates_valid_product(self) -> None:
        """正常な値で商品が生成されること."""
        product = Product(id="P001", name="Tシャツ", price=2000, stock=10)
        assert product.id == "P001"
        assert product.name == "Tシャツ"
        assert product.price == 2000
        assert product.stock == 10

    def test_rejects_negative_price(self) -> None:
        """負の価格が拒否されること."""
        with pytest.raises(ValidationError):
            Product(id="P001", name="Tシャツ", price=-100, stock=10)

    def test_rejects_negative_stock(self) -> None:
        """負の在庫数が拒否されること."""
        with pytest.raises(ValidationError):
            Product(id="P001", name="Tシャツ", price=2000, stock=-1)

    def test_allows_zero_price(self) -> None:
        """価格0が許容されること."""
        product = Product(id="P001", name="サンプル", price=0, stock=10)
        assert product.price == 0

    def test_allows_zero_stock(self) -> None:
        """在庫0が許容されること."""
        product = Product(id="P001", name="Tシャツ", price=2000, stock=0)
        assert product.stock == 0

    def test_has_enough_stock_true(self) -> None:
        """在庫が十分な場合 True を返すこと."""
        product = Product(id="P001", name="Tシャツ", price=2000, stock=10)
        assert product.has_enough_stock(10) is True

    def test_has_enough_stock_false(self) -> None:
        """在庫が不足している場合 False を返すこと."""
        product = Product(id="P001", name="Tシャツ", price=2000, stock=5)
        assert product.has_enough_stock(6) is False

    def test_decrease_stock(self) -> None:
        """在庫が正しく減少すること."""
        product = Product(id="P001", name="Tシャツ", price=2000, stock=10)
        product.decrease_stock(3)
        assert product.stock == 7

    def test_decrease_stock_raises_on_insufficient(self) -> None:
        """在庫不足時に ValueError が発生すること."""
        product = Product(id="P001", name="Tシャツ", price=2000, stock=2)
        with pytest.raises(ValueError, match="在庫が不足しています"):
            product.decrease_stock(5)
        assert product.stock == 2


# ===================================================================
# CartItem
# ===================================================================


class TestCartItem:
    """CartItem のテスト."""

    def test_creates_valid_cart_item(self) -> None:
        """正常な値でカートアイテムが生成されること."""
        item = CartItem(product_id="P001", quantity=3)
        assert item.product_id == "P001"
        assert item.quantity == 3

    def test_rejects_zero_quantity(self) -> None:
        """数量0が拒否されること."""
        with pytest.raises(ValidationError):
            CartItem(product_id="P001", quantity=0)

    def test_rejects_negative_quantity(self) -> None:
        """負の数量が拒否されること."""
        with pytest.raises(ValidationError):
            CartItem(product_id="P001", quantity=-1)


# ===================================================================
# Cart
# ===================================================================


class TestCart:
    """Cart エンティティのテスト."""

    def test_new_cart_is_empty(self) -> None:
        """新しいカートは空であること."""
        cart = Cart(user_id="user1")
        assert cart.is_empty is True
        assert cart.items == []

    def test_add_item(self) -> None:
        """商品が追加されること."""
        cart = Cart(user_id="user1")
        cart.add_item("P001", 2)
        assert len(cart.items) == 1
        assert cart.items[0].product_id == "P001"
        assert cart.items[0].quantity == 2
        assert cart.is_empty is False

    def test_add_item_increases_quantity(self) -> None:
        """同じ商品を追加すると数量が加算されること."""
        cart = Cart(user_id="user1")
        cart.add_item("P001", 2)
        cart.add_item("P001", 3)
        assert len(cart.items) == 1
        assert cart.items[0].quantity == 5

    def test_add_multiple_items(self) -> None:
        """異なる商品が別々に追加されること."""
        cart = Cart(user_id="user1")
        cart.add_item("P001", 1)
        cart.add_item("P002", 2)
        assert len(cart.items) == 2

    def test_remove_item(self) -> None:
        """商品が削除されること."""
        cart = Cart(user_id="user1")
        cart.add_item("P001", 1)
        cart.add_item("P002", 2)
        cart.remove_item("P001")
        assert len(cart.items) == 1
        assert cart.items[0].product_id == "P002"

    def test_remove_item_raises_on_nonexistent(self) -> None:
        """存在しない商品の削除で ValueError が発生すること."""
        cart = Cart(user_id="user1")
        cart.add_item("P001", 1)
        with pytest.raises(ValueError, match="カートにありません"):
            cart.remove_item("P999")

    def test_clear(self) -> None:
        """カートが空になること."""
        cart = Cart(user_id="user1")
        cart.add_item("P001", 1)
        cart.add_item("P002", 2)
        cart.clear()
        assert cart.is_empty is True
        assert cart.items == []


# ===================================================================
# CartDetailItem / CartDetails
# ===================================================================


class TestCartDetails:
    """CartDetailItem / CartDetails (frozen) のテスト."""

    def test_creates_cart_detail_item(self) -> None:
        """正常な値でカート詳細アイテムが生成されること."""
        item = CartDetailItem(
            product_id="P001",
            name="Tシャツ",
            price=2000,
            quantity=2,
            item_total=4000,
        )
        assert item.item_total == 4000

    def test_creates_cart_details(self) -> None:
        """正常な値でカート詳細が生成されること."""
        detail = CartDetails(
            items=[
                CartDetailItem(
                    product_id="P001",
                    name="Tシャツ",
                    price=2000,
                    quantity=2,
                    item_total=4000,
                ),
            ],
            subtotal=4000,
            tax=400,
            total=4400,
        )
        assert detail.subtotal == 4000
        assert detail.tax == 400
        assert detail.total == 4400

    def test_cart_details_is_frozen(self) -> None:
        """CartDetails がイミュータブルであること."""
        detail = CartDetails(items=[], subtotal=0, tax=0, total=0)
        with pytest.raises(ValidationError):
            setattr(detail, "subtotal", 100)  # noqa: B010


# ===================================================================
# OrderItem / Order
# ===================================================================


class TestOrderItem:
    """OrderItem (frozen) のテスト."""

    def test_creates_valid_order_item(self) -> None:
        """正常な値で注文アイテムが生成されること."""
        item = OrderItem(
            product_id="P001",
            name="Tシャツ",
            price=2000,
            quantity=2,
            subtotal=4000,
        )
        assert item.subtotal == 4000

    def test_order_item_is_frozen(self) -> None:
        """OrderItem がイミュータブルであること."""
        item = OrderItem(
            product_id="P001",
            name="Tシャツ",
            price=2000,
            quantity=1,
            subtotal=2000,
        )
        with pytest.raises(ValidationError):
            setattr(item, "quantity", 5)  # noqa: B010

    def test_rejects_zero_quantity(self) -> None:
        """数量0が拒否されること."""
        with pytest.raises(ValidationError):
            OrderItem(
                product_id="P001",
                name="Tシャツ",
                price=2000,
                quantity=0,
                subtotal=0,
            )


class TestOrder:
    """Order エンティティ (frozen) のテスト."""

    def test_create_calculates_totals(self) -> None:
        """Order.create が小計・消費税・合計を正しく計算すること."""
        items = [
            OrderItem(
                product_id="P001",
                name="Tシャツ",
                price=2000,
                quantity=2,
                subtotal=4000,
            ),
            OrderItem(
                product_id="P003",
                name="ステッカー",
                price=500,
                quantity=3,
                subtotal=1500,
            ),
        ]
        now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
        order = Order.create(
            order_id="ORD-0001",
            user_id="user1",
            items=items,
            created_at=now,
        )

        assert order.subtotal == 5500
        assert order.tax == 550
        assert order.total == 6050
        assert order.created_at == now

    def test_create_empty_items(self) -> None:
        """空のアイテムリストでも Order.create が動作すること."""
        order = Order.create(
            order_id="ORD-0001",
            user_id="user1",
            items=[],
            created_at=datetime(2025, 1, 1, tzinfo=UTC),
        )
        assert order.subtotal == 0
        assert order.tax == 0
        assert order.total == 0

    def test_create_uses_current_time_when_not_specified(self) -> None:
        """created_at を省略した場合、現在時刻が使用されること."""
        order = Order.create(
            order_id="ORD-0001",
            user_id="user1",
            items=[],
        )
        assert isinstance(order.created_at, datetime)

    def test_order_is_frozen(self) -> None:
        """Order がイミュータブルであること."""
        order = Order.create(
            order_id="ORD-0001",
            user_id="user1",
            items=[],
            created_at=datetime(2025, 1, 1, tzinfo=UTC),
        )
        with pytest.raises(ValidationError):
            setattr(order, "total", 9999)  # noqa: B010
