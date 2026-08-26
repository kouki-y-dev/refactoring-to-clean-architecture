"""商品リポジトリモジュール.

商品の永続化および検索を担当するリポジトリクラスを提供します。
"""

from domain.entity import Product


class ProductRepository:
    """
    商品リポジトリ (インメモリ実装).

    商品データの保存・取得・検索をコレクションのように扱います。

    Parameters
    ----------
    products : dict[str, Product] | None, optional
        初期商品データ。省略時はデフォルト商品データがロードされます。
    """

    def __init__(self, products: dict[str, Product] | None = None) -> None:
        if products is None:
            self._products: dict[str, Product] = {
                "P001": Product(
                    id="P001", name="Tシャツ", price=2000, stock=10
                ),
                "P002": Product(
                    id="P002", name="マグカップ", price=1500, stock=5
                ),
                "P003": Product(
                    id="P003", name="ステッカー", price=500, stock=20
                ),
            }
        else:
            self._products = products.copy()

    def find_all(self) -> list[Product]:
        """
        全ての商品を取得する.

        Returns
        -------
        list[Product]
            商品エンティティのリスト。
        """
        return list(self._products.values())

    def find_by_id(self, product_id: str) -> Product | None:
        """
        商品IDを指定して商品を取得する.

        Parameters
        ----------
        product_id : str
            取得対象の商品ID。

        Returns
        -------
        Product | None
            商品が存在すれば Product、存在しなければ None。
        """
        return self._products.get(product_id)

    def save(self, product: Product) -> None:
        """
        商品を保存 (追加または更新) する.

        Parameters
        ----------
        product : Product
            保存する商品エンティティ。
        """
        self._products[product.id] = product
