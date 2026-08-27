"""カートゲートウェイのインメモリ具象実装."""

from typing import TYPE_CHECKING

from domain.gateway import ICartGateway

from infrastructure.mapper.data_mapper import CartDataMapper

if TYPE_CHECKING:
    from domain.entity import Cart

    from infrastructure.persistence.models import CartRecord


class InMemoryCartGateway(ICartGateway):
    """インメモリカートデータアクセスゲートウェイ.

    内部ではストレージモデルである CartRecord を辞書で保持し、
    ドメイン層とのやり取り時に CartDataMapper で変換します。
    """

    def __init__(self, records: dict[str, CartRecord] | None = None) -> None:
        self._storage: dict[str, CartRecord] = (
            records.copy() if records is not None else {}
        )

    def find_by_user_id(self, user_id: str) -> Cart | None:
        """ユーザーIDでカートを検索する.

        Parameters
        ----------
        user_id : str
            検索するユーザーID。

        Returns
        -------
        Cart | None
            該当するカートエンティティ。存在しない場合は None。
        """
        record = self._storage.get(user_id)
        if record is None:
            return None
        return CartDataMapper.to_entity(record)

    def get_or_create(self, user_id: str) -> Cart:
        """ユーザーIDのカートを取得する。存在しない場合は新規作成する.

        Parameters
        ----------
        user_id : str
            ユーザーID。

        Returns
        -------
        Cart
            取得または新規作成されたカートエンティティ。
        """
        cart = self.find_by_user_id(user_id)
        if cart is None:
            from domain.entity import Cart

            cart = Cart(user_id=user_id)
        return cart

    def save(self, cart: Cart) -> None:
        """カート情報を保存・更新する.

        Parameters
        ----------
        cart : Cart
            保存するカートエンティティ。
        """
        record = CartDataMapper.to_record(cart)
        self._storage[cart.user_id] = record
