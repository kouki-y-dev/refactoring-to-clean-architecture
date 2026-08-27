"""カート表示・詳細取得ユースケースモジュール."""

from typing import TYPE_CHECKING

from domain.entity import TAX_RATE, CartDetailItem, CartDetails

if TYPE_CHECKING:
    from domain.repository import ICartRepository, IProductRepository


class ViewCartUseCase:
    """カートの詳細情報を取得・計算するユースケース.

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
        """カートの詳細と合計金額を計算して返す.

        カートが空の場合は None を返す。

        Parameters
        ----------
        user_id : str
            ユーザーID。

        Returns
        -------
        CartDetails | None
            カート詳細。カートが空の場合は None。
        """
        cart = self.cart_repo.find_by_user_id(user_id)
        if cart is None or cart.is_empty:
            return None

        detail_items: list[CartDetailItem] = []
        subtotal = 0

        for item in cart.items:
            product = self.product_repo.find_by_id(item.product_id)
            if product is None:
                continue

            item_total = product.price * item.quantity
            detail_items.append(
                CartDetailItem(
                    product_id=item.product_id,
                    name=product.name,
                    price=product.price,
                    quantity=item.quantity,
                    item_total=item_total,
                )
            )
            subtotal += item_total

        tax = int(subtotal * TAX_RATE)
        total = subtotal + tax

        return CartDetails(
            items=detail_items,
            subtotal=subtotal,
            tax=tax,
            total=total,
        )
