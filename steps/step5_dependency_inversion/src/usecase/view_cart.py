"""カート表示・集計ユースケースモジュール."""

from typing import TYPE_CHECKING

from domain.entity import TAX_RATE, CartDetailItem, CartDetails

if TYPE_CHECKING:
    from domain.repository import ICartRepository, IProductRepository


class ViewCartUseCase:
    """カートの内容を取得・集計するユースケース.

    Parameters
    ----------
    cart_repo : ICartRepository
        カートリポジトリインターフェース。
    product_repo : IProductRepository
        商品リポジトリインターフェース。
    """

    def __init__(
        self,
        cart_repo: ICartRepository,
        product_repo: IProductRepository,
    ) -> None:
        self.cart_repo = cart_repo
        self.product_repo = product_repo

    def execute(self, user_id: str) -> CartDetails | None:
        """カートの内容を取得し、小計・消費税・合計を計算して返す.

        Parameters
        ----------
        user_id : str
            ユーザーID。

        Returns
        -------
        CartDetails | None
            カート詳細。カートが空または存在しない場合は None。
        """
        cart = self.cart_repo.find_by_user_id(user_id)
        if cart is None or cart.is_empty:
            return None

        items: list[CartDetailItem] = []
        subtotal = 0

        for cart_item in cart.items:
            product = self.product_repo.find_by_id(cart_item.product_id)
            if product is None:
                continue

            item_total = product.price * cart_item.quantity
            subtotal += item_total
            items.append(
                CartDetailItem(
                    product_id=cart_item.product_id,
                    name=product.name,
                    price=product.price,
                    quantity=cart_item.quantity,
                    item_total=item_total,
                )
            )

        tax = int(subtotal * TAX_RATE)
        total = subtotal + tax

        return CartDetails(
            items=items,
            subtotal=subtotal,
            tax=tax,
            total=total,
        )
