"""商品一覧取得ユースケースモジュール."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.entity import Product
    from domain.repository import IProductRepository


class ListProductsUseCase:
    """商品一覧を取得するユースケース.

    Parameters
    ----------
    product_repo : IProductRepository
        商品リポジトリインターフェース。
    """

    def __init__(self, product_repo: IProductRepository) -> None:
        self.product_repo = product_repo

    def execute(self) -> list[Product]:
        """全商品を取得する.

        Returns
        -------
        list[Product]
            商品エンティティのリスト。
        """
        return self.product_repo.find_all()
