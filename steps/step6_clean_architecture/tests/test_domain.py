"""Step 6: ドメインモデル単体テスト.

Product, Cart, CartItem, Order, OrderItem, CartDetails, CartDetailItem
のエンティティおよび値オブジェクトの振る舞い・計算・バリデーションを検証します。
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
# Product エンティティのテスト
# ===================================================================


class TestProduct:
    """Product エンティティのテスト."""

    def test_creates_product(self) -> None:
        """正常な値で Product が生成されること."""
        p = Product(id="P001", name="Tシャツ", price=2000, stock=10)
        assert p.id == "P001"
        assert p.name == "Tシャツ"
        assert p.price == 2000
        assert p.stock == 10

    def test_has_enough_stock(self) -> None:
        """在庫が足りているか判定できること."""
        p = Product(id="P001", name="Tシャツ", price=2000, stock=5)
        assert p.has_enough_stock(3) is True
        assert p.has_enough_stock(5) is True
        assert p.has_enough_stock(6) is False

    def test_decrease_stock(self) -> None:
        """在庫を減算できること."""
        p = Product(id="P001", name="Tシャツ", price=2000, stock=5)
        p.decrease_stock(3)
        assert p.stock == 2

    def test_decrease_stock_insufficient(self) -> None:
        """在庫不足時に ValueError が送出されること."""
        p = Product(id="P001", name="Tシャツ", price=2000, stock=2)
        with pytest.raises(ValueError, match="在庫が不足しています"):
            p.decrease_stock(3)

    def test_rejects_negative_price(self) -> None:
        """負の価格が拒否されること."""
        with pytest.raises(ValidationError):
            Product(id="P001", name="Tシャツ", price=-100, stock=10)

    def test_rejects_negative_stock(self) -> None:
        """負の在庫数が拒否されること."""
        with pytest.raises(ValidationError):
            Product(id="P001", name="Tシャツ", price=2000, stock=-1)


# ===================================================================
# CartItem / Cart
# ===================================================================


class TestCartItem:
    """CartItem のテスト."""

    def test_creates_cart_item(self) -> None:
        """正常な値で CartItem が生成されること."""
        item = CartItem(product_id="P001", quantity=2)
        assert item.product_id == "P001"
        assert item.quantity == 2

    def test_rejects_zero_or_negative_quantity(self) -> None:
        """0以下の数量が拒否されること."""
        with pytest.raises(ValidationError):
            CartItem(product_id="P001", quantity=0)
        with pytest.raises(ValidationError):
            CartItem(product_id="P001", quantity=-1)


class TestCart:
    """Cart エンティティのテスト."""

    def test_creates_empty_cart(self) -> None:
        """初期状態で空のカートが生成されること."""
        cart = Cart(user_id="user1")
        assert cart.user_id == "user1"
        assert cart.items == []
        assert cart.is_empty is True

    def test_add_item_new(self) -> None:
        """新しい商品がカートに追加されること."""
        cart = Cart(user_id="user1")
        cart.add_item("P001", 2)
        assert len(cart.items) == 1
        assert cart.items[0].product_id == "P001"
        assert cart.items[0].quantity == 2
        assert cart.is_empty is False

    def test_add_item_existing(self) -> None:
        """既存商品を追加した場合、数量が加算されること."""
        cart = Cart(user_id="user1")
        cart.add_item("P001", 2)
        cart.add_item("P001", 3)
        assert len(cart.items) == 1
        assert cart.items[0].quantity == 5

    def test_remove_item_success(self) -> None:
        """商品がカートから削除されること."""
        cart = Cart(user_id="user1")
        cart.add_item("P001", 2)
        cart.add_item("P002", 1)
        cart.remove_item("P001")
        assert len(cart.items) == 1
        assert cart.items[0].product_id == "P002"

    def test_remove_item_not_in_cart(self) -> None:
        """カート外の削除で ValueError が送出されること."""
        cart = Cart(user_id="user1")
        with pytest.raises(ValueError, match="カートにありません"):
            cart.remove_item("P001")

    def test_clear(self) -> None:
        """カートが空にクリアされること."""
        cart = Cart(user_id="user1")
        cart.add_item("P001", 2)
        cart.clear()
        assert cart.is_empty is True
        assert len(cart.items) == 0


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
