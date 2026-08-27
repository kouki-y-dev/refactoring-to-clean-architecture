"""カート追加ユースケースモジュール."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.entity import Product
    from domain.repository import ICartRepository, IProductRepository


class AddToCartUseCase:
    """カートに商品を追加するユースケース.

    Parameters
    ----------
    product_repo : IProductRepository
        商品リポジトリインターフェース。
    cart_repo : ICartRepository
        カートリポジトリインターフェース。
    """

    def __init__(
        self,
        product_repo: IProductRepository,
        cart_repo: ICartRepository,
    ) -> None:
        self.product_repo = product_repo
        self.cart_repo = cart_repo

    def execute(self, user_id: str, product_id: str, quantity: int) -> Product:
        """商品をカートに追加し、更新されたカートを保存する.

        Parameters
        ----------
        user_id : str
            ユーザーID。
        product_id : str
            追加する商品ID。
        quantity : int
            追加する数量。

        Returns
        -------
        Product
            カートに追加された商品エンティティ。

        Raises
        ------
        ValueError
            商品が存在しない、または在庫が不足している場合。
        """
        product = self.product_repo.find_by_id(product_id)
        if product is None:
            msg = f"エラー: 商品 {product_id} が見つかりません"
            raise ValueError(msg)

        if not product.has_enough_stock(quantity):
            msg = (
                f"エラー: {product.name} の在庫が不足しています"
                f"(残り {product.stock}個)"
            )
            raise ValueError(msg)

        cart = self.cart_repo.get_or_create(user_id)
        cart.add_item(product_id, quantity)
        self.cart_repo.save(cart)

        return product
