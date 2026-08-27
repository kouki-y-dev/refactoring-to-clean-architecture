"""商品ゲートウェイのインメモリ具象実装."""

from typing import TYPE_CHECKING

from domain.gateway import IProductGateway

from infrastructure.mapper.data_mapper import ProductDataMapper
from infrastructure.persistence.models import ProductRecord

if TYPE_CHECKING:
    from domain.entity import Product

# 初期商品データ (Step 4, 5, 6 と共通)
INITIAL_PRODUCTS: list[ProductRecord] = [
    ProductRecord(id="P001", name="Tシャツ", price=2000, stock=10),
    ProductRecord(id="P002", name="マグカップ", price=1200, stock=5),
    ProductRecord(id="P003", name="ステッカー", price=500, stock=20),
]


class InMemoryProductGateway(IProductGateway):
    """インメモリ商品データアクセスゲートウェイ.

    内部ではストレージモデルである ProductRecord を辞書で保持し、
    ドメイン層とのやり取り時に ProductDataMapper で変換します。
    """

    def __init__(
        self, records: dict[str, ProductRecord] | None = None
    ) -> None:
        if records is not None:
            self._storage: dict[str, ProductRecord] = records.copy()
        else:
            self._storage = {p.id: p for p in INITIAL_PRODUCTS}

    def find_all(self) -> list[Product]:
        """全商品を取得する.

        Returns
        -------
        list[Product]
            商品エンティティのリスト。
        """
        return [
            ProductDataMapper.to_entity(record)
            for record in self._storage.values()
        ]

    def find_by_id(self, product_id: str) -> Product | None:
        """商品IDで商品を検索する.

        Parameters
        ----------
        product_id : str
            検索する商品ID。

        Returns
        -------
        Product | None
            該当する商品エンティティ。存在しない場合は None。
        """
        record = self._storage.get(product_id)
        if record is None:
            return None
        return ProductDataMapper.to_entity(record)

    def save(self, product: Product) -> None:
        """商品情報を保存・更新する.

        Parameters
        ----------
        product : Product
            保存する商品エンティティ。
        """
        record = ProductDataMapper.to_record(product)
        self._storage[product.id] = record
