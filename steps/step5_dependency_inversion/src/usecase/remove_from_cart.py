"""カート削除ユースケースモジュール."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.repository import ICartRepository


class RemoveFromCartUseCase:
    """カートから商品を削除するユースケース.

    Parameters
    ----------
    cart_repo : ICartRepository
        カートリポジトリインターフェース。
    """

    def __init__(self, cart_repo: ICartRepository) -> None:
        self.cart_repo = cart_repo

    def execute(self, user_id: str, product_id: str) -> None:
        """カートから商品を削除する.

        カートが空でないこと、および商品がカート内に存在することを確認します。

        Parameters
        ----------
        user_id : str
            ユーザーID。
        product_id : str
            削除する商品ID。

        Raises
        ------
        ValueError
            カートが存在しないか空の場合、または商品がカートに存在しない場合。
        """
        cart = self.cart_repo.find_by_user_id(user_id)
        if cart is None or cart.is_empty:
            msg = "エラー: カートが空です"
            raise ValueError(msg)

        cart.remove_item(product_id)
        self.cart_repo.save(cart)
