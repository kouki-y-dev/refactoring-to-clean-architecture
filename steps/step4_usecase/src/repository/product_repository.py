"""商品リポジトリモジュール.

Product エンティティのデータアクセス・永続化をコレクションのように扱います。
"""

from domain.entity import Product

INITIAL_PRODUCTS: dict[str, Product] = {
    "P001": Product(id="P001", name="Tシャツ", price=2000, stock=10),
    "P002": Product(id="P002", name="マグカップ", price=1200, stock=5),
    "P003": Product(id="P003", name="ステッカー", price=500, stock=20),
}


class ProductRepository:
    """商品リポジトリ.

    Parameters
    ----------
    products : dict[str, Product] | None, optional
        初期商品データ。省略時は初期マスタデータを使用。
    """

    def __init__(self, products: dict[str, Product] | None = None) -> None:
        if products is None:
            self._products = {
                k: v.model_copy() for k, v in INITIAL_PRODUCTS.items()
            }
        else:
            self._products = products

    def find_all(self) -> list[Product]:
        """全商品を取得する.

        Returns
        -------
        list[Product]
            商品エンティティのリスト。
        """
        return list(self._products.values())

    def find_by_id(self, product_id: str) -> Product | None:
        """商品IDによって商品を検索する.

        Parameters
        ----------
        product_id : str
            検索する商品ID。

        Returns
        -------
        Product | None
            商品エンティティ。存在しない場合は None。
        """
        return self._products.get(product_id)

    def save(self, product: Product) -> None:
        """商品を保存・更新する.

        Parameters
        ----------
        product : Product
            保存する商品エンティティ。
        """
        self._products[product.id] = product
