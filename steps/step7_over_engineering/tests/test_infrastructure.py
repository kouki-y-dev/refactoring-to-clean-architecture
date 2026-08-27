"""Infrastructure layer tests for Step 7."""

from datetime import datetime
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from domain.entity import Cart, CartItem, Order, OrderItem, Product
from infrastructure.gateway.product_gateway import (
    INITIAL_PRODUCTS,
    InMemoryProductGateway,
)
from infrastructure.mapper.data_mapper import (
    CartDataMapper,
    OrderDataMapper,
    ProductDataMapper,
)
from infrastructure.persistence.models import (
    CartItemRecord,
    CartRecord,
    OrderItemRecord,
    OrderRecord,
    ProductRecord,
)

if TYPE_CHECKING:
    from infrastructure.gateway.cart_gateway import InMemoryCartGateway
    from infrastructure.gateway.order_gateway import InMemoryOrderGateway


class TestProductDataMapper:
    """ProductDataMapper のテスト."""

    def test_to_entity(self) -> None:
        record = ProductRecord(id="P001", name="Tシャツ", price=2000, stock=10)
        entity = ProductDataMapper.to_entity(record)
        assert entity.id == "P001"
        assert entity.name == "Tシャツ"
        assert entity.price == 2000
        assert entity.stock == 10

    def test_to_record(self) -> None:
        entity = Product(id="P001", name="Tシャツ", price=2000, stock=10)
        record = ProductDataMapper.to_record(entity)
        assert record.id == "P001"
        assert record.name == "Tシャツ"
        assert record.price == 2000
        assert record.stock == 10


class TestCartDataMapper:
    """CartDataMapper のテスト."""

    def test_to_entity(self) -> None:
        record = CartRecord(
            user_id="user1",
            items=[CartItemRecord(product_id="P001", quantity=2)],
        )
        entity = CartDataMapper.to_entity(record)
        assert entity.user_id == "user1"
        assert len(entity.items) == 1
        assert entity.items[0].product_id == "P001"
        assert entity.items[0].quantity == 2

    def test_to_record(self) -> None:
        entity = Cart(
            user_id="user1", items=[CartItem(product_id="P001", quantity=2)]
        )
        record = CartDataMapper.to_record(entity)
        assert record.user_id == "user1"
        assert len(record.items) == 1
        assert record.items[0].product_id == "P001"
        assert record.items[0].quantity == 2


class TestOrderDataMapper:
    """OrderDataMapper のテスト."""

    def test_to_entity_and_to_record(self) -> None:
        now = datetime(2026, 1, 1, 12, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
        record = OrderRecord(
            order_id="ord_001",
            user_id="user1",
            items=[
                OrderItemRecord(
                    product_id="P001",
                    name="Tシャツ",
                    price=2000,
                    quantity=1,
                    subtotal=2000,
                )
            ],
            subtotal=2000,
            tax=200,
            total=2200,
            created_at=now,
        )
        entity = OrderDataMapper.to_entity(record)
        assert entity.order_id == "ord_001"
        assert entity.total == 2200
        assert entity.created_at == now

        converted_record = OrderDataMapper.to_record(entity)
        assert converted_record.order_id == "ord_001"
        assert converted_record.total == 2200
        assert len(converted_record.items) == 1


class TestInMemoryProductGateway:
    """InMemoryProductGateway のテスト."""

    def test_find_all(self, product_gateway: InMemoryProductGateway) -> None:
        products = product_gateway.find_all()
        assert len(products) == len(INITIAL_PRODUCTS)

    def test_custom_records_init(self) -> None:
        custom_record = ProductRecord(
            id="P999", name="限定品", price=5000, stock=1
        )
        custom_gateway = InMemoryProductGateway(
            records={"P999": custom_record}
        )
        products = custom_gateway.find_all()
        assert len(products) == 1
        assert products[0].id == "P999"

    def test_find_by_id_found(
        self, product_gateway: InMemoryProductGateway
    ) -> None:
        product = product_gateway.find_by_id("P001")
        assert product is not None
        assert product.id == "P001"
        assert product.name == "Tシャツ"

    def test_find_by_id_not_found(
        self, product_gateway: InMemoryProductGateway
    ) -> None:
        product = product_gateway.find_by_id("nonexistent")
        assert product is None

    def test_save(self, product_gateway: InMemoryProductGateway) -> None:
        product = Product(
            id="P001", name="Tシャツ (更新)", price=2500, stock=8
        )
        product_gateway.save(product)
        saved = product_gateway.find_by_id("P001")
        assert saved is not None
        assert saved.name == "Tシャツ (更新)"
        assert saved.price == 2500
        assert saved.stock == 8


class TestInMemoryCartGateway:
    """InMemoryCartGateway のテスト."""

    def test_find_by_user_id_empty(
        self, cart_gateway: InMemoryCartGateway
    ) -> None:
        cart = cart_gateway.find_by_user_id("user1")
        assert cart is None

    def test_get_or_create(self, cart_gateway: InMemoryCartGateway) -> None:
        cart = cart_gateway.get_or_create("user1")
        assert cart.user_id == "user1"
        assert cart.is_empty is True

    def test_save_and_find(self, cart_gateway: InMemoryCartGateway) -> None:
        cart = Cart(user_id="user1")
        cart.add_item("P001", 2)
        cart_gateway.save(cart)

        saved = cart_gateway.find_by_user_id("user1")
        assert saved is not None
        assert saved.user_id == "user1"
        assert len(saved.items) == 1
        assert saved.items[0].product_id == "P001"
        assert saved.items[0].quantity == 2


class TestInMemoryOrderGateway:
    """InMemoryOrderGateway のテスト."""

    def test_find_by_user_id_empty(
        self, order_gateway: InMemoryOrderGateway
    ) -> None:
        orders = order_gateway.find_by_user_id("user1")
        assert orders == []

    def test_save_and_find(self, order_gateway: InMemoryOrderGateway) -> None:
        now = datetime(2026, 1, 1, 12, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
        order = Order.create(
            order_id="ord_001",
            user_id="user1",
            items=[
                OrderItem(
                    product_id="P001",
                    name="Tシャツ",
                    price=2000,
                    quantity=1,
                    subtotal=2000,
                )
            ],
            created_at=now,
        )
        order_gateway.save(order)

        orders = order_gateway.find_by_user_id("user1")
        assert len(orders) == 1
        assert orders[0].order_id == "ord_001"

    def test_next_order_id(self, order_gateway: InMemoryOrderGateway) -> None:
        assert order_gateway.next_order_id() == "ord_001"
        assert order_gateway.next_order_id() == "ord_002"
        assert order_gateway.next_order_id() == "ord_003"
