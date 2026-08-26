"""注文確定ユースケースモジュール."""

from typing import TYPE_CHECKING

from domain.entity import Order, OrderItem

if TYPE_CHECKING:
    from domain.repository import (
        ICartRepository,
        IOrderRepository,
        IProductRepository,
    )


class PlaceOrderUseCase:
    """注文を確定するユースケース.

    Parameters
    ----------
    cart_repo : ICartRepository
        カートリポジトリインターフェース。
    product_repo : IProductRepository
        商品リポジトリインターフェース。
    order_repo : IOrderRepository
        注文リポジトリインターフェース。
    """

    def __init__(
        self,
        cart_repo: ICartRepository,
        product_repo: IProductRepository,
        order_repo: IOrderRepository,
    ) -> None:
        self.cart_repo = cart_repo
        self.product_repo = product_repo
        self.order_repo = order_repo

    def execute(self, user_id: str) -> Order:
        """注文を確定する.

        在庫チェック・注文作成・在庫減少・カートクリアを行い、注文エンティティを保存します。

        Parameters
        ----------
        user_id : str
            ユーザーID。

        Returns
        -------
        Order
            作成・保存された注文エンティティ。

        Raises
        ------
        ValueError
            カートが存在しないか空の場合、または在庫が不足している場合。
        """
        cart = self.cart_repo.find_by_user_id(user_id)
        if cart is None or cart.is_empty:
            msg = "エラー: カートが空です"
            raise ValueError(msg)

        # 1. 在庫チェック
        for cart_item in cart.items:
            product = self.product_repo.find_by_id(cart_item.product_id)
            if product is None:
                msg = f"エラー: 商品 {cart_item.product_id} が見つかりません"
                raise ValueError(msg)

            if not product.has_enough_stock(cart_item.quantity):
                msg = (
                    f"エラー: {product.name} の在庫が不足しています"
                    f"(残り {product.stock}個)"
                )
                raise ValueError(msg)

        # 2. 注文明細アイテムの作成
        order_items: list[OrderItem] = []
        for cart_item in cart.items:
            product = self.product_repo.find_by_id(cart_item.product_id)
            if product is None:
                continue

            item_total = product.price * cart_item.quantity
            order_items.append(
                OrderItem(
                    product_id=cart_item.product_id,
                    name=product.name,
                    price=product.price,
                    quantity=cart_item.quantity,
                    subtotal=item_total,
                )
            )

        # 3. 注文エンティティの作成 (ドメインファクトリに計算を委譲)
        order_id = self.order_repo.next_order_id()
        order = Order.create(
            order_id=order_id,
            user_id=user_id,
            items=order_items,
        )

        # 4. 注文の永続化
        self.order_repo.save(order)

        # 5. 在庫の減少と更新
        for cart_item in cart.items:
            product = self.product_repo.find_by_id(cart_item.product_id)
            if product is not None:
                product.decrease_stock(cart_item.quantity)
                self.product_repo.save(product)

        # 6. カートのクリアと永続化
        cart.clear()
        self.cart_repo.save(cart)

        return order
