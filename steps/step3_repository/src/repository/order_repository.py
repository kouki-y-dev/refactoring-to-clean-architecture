"""注文リポジトリモジュール.

注文エンティティの永続化および検索を担当するリポジトリクラスを提供します。
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.entity import Order


class OrderRepository:
    """
    注文リポジトリ (インメモリ実装).

    注文エンティティの保存・取得・検索をコレクションのように扱います。

    Parameters
    ----------
    orders : dict[str, Order] | None, optional
        初期注文データ。
    """

    def __init__(self, orders: dict[str, Order] | None = None) -> None:
        if orders is None:
            self._orders: dict[str, Order] = {}
        else:
            self._orders = orders.copy()

    def save(self, order: Order) -> None:
        """
        注文を保存する.

        Parameters
        ----------
        order : Order
            保存する注文エンティティ。
        """
        self._orders[order.order_id] = order

    def find_by_id(self, order_id: str) -> Order | None:
        """
        注文IDを指定して注文を取得する.

        Parameters
        ----------
        order_id : str
            注文ID。

        Returns
        -------
        Order | None
            注文が存在すれば Order、存在しなければ None。
        """
        return self._orders.get(order_id)

    def find_by_user_id(self, user_id: str) -> list[Order]:
        """
        ユーザーIDに紐づく注文一覧を取得する.

        Parameters
        ----------
        user_id : str
            ユーザーID。

        Returns
        -------
        list[Order]
            該当ユーザーの注文リスト。
        """
        return [
            order
            for order in self._orders.values()
            if order.user_id == user_id
        ]

    def find_all(self) -> list[Order]:
        """
        全ての注文を取得する.

        Returns
        -------
        list[Order]
            注文エンティティのリスト。
        """
        return list(self._orders.values())

    def count(self) -> int:
        """
        保存されている注文総数を取得する.

        Returns
        -------
        int
            注文総数。
        """
        return len(self._orders)

    def next_order_id(self) -> str:
        """
        次の注文IDを採番する.

        Returns
        -------
        str
            採番された注文ID (例: 'ORD-0001') 。
        """
        return f"ORD-{len(self._orders) + 1:04d}"
