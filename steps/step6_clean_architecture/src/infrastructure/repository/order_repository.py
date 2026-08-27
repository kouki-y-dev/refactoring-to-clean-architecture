"""注文リポジトリ具象実装モジュール.

Order エンティティのデータアクセス・永続化をインメモリ辞書として実装します。
IOrderRepository インターフェースを満たします。
"""

from typing import TYPE_CHECKING

from domain.repository import IOrderRepository

if TYPE_CHECKING:
    from domain.entity import Order


class InMemoryOrderRepository(IOrderRepository):
    """注文リポジトリのインメモリ実装.

    Parameters
    ----------
    orders : dict[str, Order] | None, optional
        初期注文データ。省略時は空の辞書を使用。
    """

    def __init__(self, orders: dict[str, Order] | None = None) -> None:
        self._orders: dict[str, Order] = orders if orders is not None else {}

    def save(self, order: Order) -> None:
        """注文を保存する.

        Parameters
        ----------
        order : Order
            保存する注文エンティティ。
        """
        self._orders[order.order_id] = order

    def find_by_id(self, order_id: str) -> Order | None:
        """注文IDによって注文を検索する.

        Parameters
        ----------
        order_id : str
            検索する注文ID。

        Returns
        -------
        Order | None
            注文エンティティ。存在しない場合は None。
        """
        return self._orders.get(order_id)

    def find_by_user_id(self, user_id: str) -> list[Order]:
        """ユーザーIDに紐づく注文履歴を取得する.

        Parameters
        ----------
        user_id : str
            ユーザーID。

        Returns
        -------
        list[Order]
            ユーザーの注文エンティティのリスト。
        """
        return [
            order
            for order in self._orders.values()
            if order.user_id == user_id
        ]

    def find_all(self) -> list[Order]:
        """全注文を取得する.

        Returns
        -------
        list[Order]
            全注文エンティティのリスト。
        """
        return list(self._orders.values())

    def count(self) -> int:
        """保存されている注文の総数を返す.

        Returns
        -------
        int
            注文総数。
        """
        return len(self._orders)

    def next_order_id(self) -> str:
        """新しい注文IDを採番する.

        Returns
        -------
        str
            新規注文ID (例: 'ORD-0001') 。
        """
        return f"ORD-{self.count() + 1:04d}"


OrderRepository = InMemoryOrderRepository
