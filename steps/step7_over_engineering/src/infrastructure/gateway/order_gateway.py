"""注文ゲートウェイのインメモリ具象実装."""

from typing import TYPE_CHECKING

from domain.gateway import IOrderGateway

from infrastructure.mapper.data_mapper import OrderDataMapper

if TYPE_CHECKING:
    from domain.entity import Order

    from infrastructure.persistence.models import OrderRecord


class InMemoryOrderGateway(IOrderGateway):
    """インメモリ注文データアクセスゲートウェイ.

    内部ではストレージモデルである OrderRecord をリストで保持し、
    ドメイン層とのやり取り時に OrderDataMapper で変換します。
    """

    def __init__(
        self,
        records: list[OrderRecord] | None = None,
        initial_order_num: int = 1,
    ) -> None:
        self._storage: list[OrderRecord] = (
            records.copy() if records is not None else []
        )
        self._order_count: int = initial_order_num

    def find_by_user_id(self, user_id: str) -> list[Order]:
        """ユーザーIDで注文履歴を検索する.

        Parameters
        ----------
        user_id : str
            検索するユーザーID。

        Returns
        -------
        list[Order]
            注文エンティティのリスト。
        """
        user_records = [
            record for record in self._storage if record.user_id == user_id
        ]
        return [OrderDataMapper.to_entity(record) for record in user_records]

    def save(self, order: Order) -> None:
        """注文情報を保存する.

        Parameters
        ----------
        order : Order
            保存する注文エンティティ。
        """
        record = OrderDataMapper.to_record(order)
        self._storage.append(record)

    def next_order_id(self) -> str:
        """新しい注文IDを採番する.

        Returns
        -------
        str
            一意の注文ID文字列。
        """
        order_id = f"ord_{self._order_count:03d}"
        self._order_count += 1
        return order_id
