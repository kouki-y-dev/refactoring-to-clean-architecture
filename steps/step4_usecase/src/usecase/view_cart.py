"""カート表示・詳細取得ユースケースモジュール."""

from typing import TYPE_CHECKING

from domain.entity import TAX_RATE, CartDetailItem, CartDetails

if TYPE_CHECKING:
    from repository.cart_repository import CartRepository
    from repository.product_repository import ProductRepository


class ViewCartUseCase:
    """カートの詳細・集計情報を取得するユースケース.

    Parameters
    ----------
    cart_repo : CartRepository
        カートリポジトリ。
    product_repo : ProductRepository
        商品リポジトリ。
    """

    def __init__(
        self,
        cart_repo: CartRepository,
        product_repo: ProductRepository,
    ) -> None:
        self.cart_repo = cart_repo
        self.product_repo = product_repo

    def execute(self, user_id: str) -> CartDetails | None:
        """カートの詳細情報と計算結果 (小計、消費税、合計) を取得する.

        Parameters
        ----------
        user_id : str
            ユーザーID。

        Returns
        -------
        CartDetails | None
            カート内の商品詳細と合計金額。カートが存在しないか空の場合は None。
        """
        cart = self.cart_repo.find_by_user_id(user_id)
        if cart is None or cart.is_empty:
            return None

        subtotal = 0
        items: list[CartDetailItem] = []
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
        return CartDetails(
            items=items,
            subtotal=subtotal,
            tax=tax,
            total=subtotal + tax,
        )
