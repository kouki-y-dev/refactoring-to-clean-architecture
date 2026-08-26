"""商品一覧取得ユースケースモジュール."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.entity import Product
    from repository.product_repository import ProductRepository


class ListProductsUseCase:
    """商品一覧を取得するユースケース.

    Parameters
    ----------
    product_repo : ProductRepository
        商品リポジトリ。
    """

    def __init__(self, product_repo: ProductRepository) -> None:
        self.product_repo = product_repo

    def execute(self) -> list[Product]:
        """全ての商品情報を取得する.

        Returns
        -------
        list[Product]
            商品エンティティのリスト。
        """
        return self.product_repo.find_all()
