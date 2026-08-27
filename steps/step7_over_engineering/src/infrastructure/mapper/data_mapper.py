"""ドメインエンティティと永続化レコード間の変換モジュール.

Data Mapper パターンを用いて相互変換を行います。
"""

from domain.entity import Cart, CartItem, Order, OrderItem, Product
from infrastructure.persistence.models import (
    CartItemRecord,
    CartRecord,
    OrderItemRecord,
    OrderRecord,
    ProductRecord,
)


class ProductDataMapper:
    """商品エンティティ ↔ 商品レコードのデータマッパー."""

    @staticmethod
    def to_entity(record: ProductRecord) -> Product:
        """ProductRecord から Product エンティティに変換する.

        Parameters
        ----------
        record : ProductRecord
            商品永続化レコード。

        Returns
        -------
        Product
            ドメインエンティティ。
        """
        return Product(
            id=record.id,
            name=record.name,
            price=record.price,
            stock=record.stock,
        )

    @staticmethod
    def to_record(entity: Product) -> ProductRecord:
        """Product エンティティから ProductRecord に変換する.

        Parameters
        ----------
        entity : Product
            ドメインエンティティ。

        Returns
        -------
        ProductRecord
            商品永続化レコード。
        """
        return ProductRecord(
            id=entity.id,
            name=entity.name,
            price=entity.price,
            stock=entity.stock,
        )


class CartDataMapper:
    """カートエンティティ ↔ カートレコードのデータマッパー."""

    @staticmethod
    def to_entity(record: CartRecord) -> Cart:
        """CartRecord から Cart エンティティに変換する.

        Parameters
        ----------
        record : CartRecord
            カート永続化レコード。

        Returns
        -------
        Cart
            ドメインエンティティ。
        """
        return Cart(
            user_id=record.user_id,
            items=[
                CartItem(product_id=item.product_id, quantity=item.quantity)
                for item in record.items
            ],
        )

    @staticmethod
    def to_record(entity: Cart) -> CartRecord:
        """Cart エンティティから CartRecord に変換する.

        Parameters
        ----------
        entity : Cart
            ドメインエンティティ。

        Returns
        -------
        CartRecord
            カート永続化レコード。
        """
        return CartRecord(
            user_id=entity.user_id,
            items=[
                CartItemRecord(
                    product_id=item.product_id, quantity=item.quantity
                )
                for item in entity.items
            ],
        )


class OrderDataMapper:
    """注文エンティティ ↔ 注文レコードのデータマッパー."""

    @staticmethod
    def to_entity(record: OrderRecord) -> Order:
        """OrderRecord から Order エンティティに変換する.

        Parameters
        ----------
        record : OrderRecord
            注文永続化レコード。

        Returns
        -------
        Order
            ドメインエンティティ。
        """
        return Order(
            order_id=record.order_id,
            user_id=record.user_id,
            items=[
                OrderItem(
                    product_id=item.product_id,
                    name=item.name,
                    price=item.price,
                    quantity=item.quantity,
                    subtotal=item.subtotal,
                )
                for item in record.items
            ],
            subtotal=record.subtotal,
            tax=record.tax,
            total=record.total,
            created_at=record.created_at,
        )

    @staticmethod
    def to_record(entity: Order) -> OrderRecord:
        """Order エンティティから OrderRecord に変換する.

        Parameters
        ----------
        entity : Order
            ドメインエンティティ。

        Returns
        -------
        OrderRecord
            注文永続化レコード。
        """
        return OrderRecord(
            order_id=entity.order_id,
            user_id=entity.user_id,
            items=[
                OrderItemRecord(
                    product_id=item.product_id,
                    name=item.name,
                    price=item.price,
                    quantity=item.quantity,
                    subtotal=item.subtotal,
                )
                for item in entity.items
            ],
            subtotal=entity.subtotal,
            tax=entity.tax,
            total=entity.total,
            created_at=entity.created_at,
        )
