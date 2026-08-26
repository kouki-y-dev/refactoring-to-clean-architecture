"""注文履歴取得ユースケースモジュール."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.entity import Order
    from repository.order_repository import OrderRepository


class GetOrderHistoryUseCase:
    """ユーザーの注文履歴を取得するユースケース.

    Parameters
    ----------
    order_repo : OrderRepository
        注文リポジトリ。
    """

    def __init__(self, order_repo: OrderRepository) -> None:
        self.order_repo = order_repo

    def execute(self, user_id: str) -> list[Order]:
        """指定されたユーザーの注文履歴を取得する.

        Parameters
        ----------
        user_id : str
            ユーザーID。

        Returns
        -------
        list[Order]
            ユーザーの注文エンティティのリスト。
        """
        return self.order_repo.find_by_user_id(user_id)
