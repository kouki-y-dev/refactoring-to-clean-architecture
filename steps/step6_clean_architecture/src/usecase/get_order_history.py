"""注文履歴取得ユースケースモジュール."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.entity import Order
    from domain.repository import IOrderRepository


class GetOrderHistoryUseCase:
    """注文履歴を取得するユースケース.

    Parameters
    ----------
    order_repo : IOrderRepository
        注文リポジトリインターフェース。
    """

    def __init__(self, order_repo: IOrderRepository) -> None:
        self.order_repo = order_repo

    def execute(self, user_id: str) -> list[Order]:
        """指定したユーザーの注文履歴を取得する.

        Parameters
        ----------
        user_id : str
            ユーザーID。

        Returns
        -------
        list[Order]
            注文エンティティのリスト。
        """
        return self.order_repo.find_by_user_id(user_id)
