"""カートリポジトリモジュール.

ユーザーのショッピングカートの永続化および検索を担当するリポジトリクラスを提供します。
"""

from domain.entity import Cart


class CartRepository:
    """
    カートリポジトリ (インメモリ実装).

    ユーザーごとのカートエンティティの保存・取得・削除をコレクションのように扱います。

    Parameters
    ----------
    carts : dict[str, Cart] | None, optional
        初期カートデータ。
    """

    def __init__(self, carts: dict[str, Cart] | None = None) -> None:
        if carts is None:
            self._carts: dict[str, Cart] = {}
        else:
            self._carts = carts.copy()

    def find_by_user_id(self, user_id: str) -> Cart | None:
        """
        ユーザーIDを指定してカートを取得する.

        Parameters
        ----------
        user_id : str
            ユーザーID。

        Returns
        -------
        Cart | None
            カートが存在すれば Cart、存在しなければ None。
        """
        return self._carts.get(user_id)

    def get_or_create(self, user_id: str) -> Cart:
        """
        ユーザーIDを指定してカートを取得する.

        存在しない場合は新しい空のカートを作成して返します。

        Parameters
        ----------
        user_id : str
            ユーザーID。

        Returns
        -------
        Cart
            ユーザーのカートエンティティ。
        """
        if user_id not in self._carts:
            self._carts[user_id] = Cart(user_id=user_id)
        return self._carts[user_id]

    def save(self, cart: Cart) -> None:
        """
        カートを保存 (追加または更新) する.

        Parameters
        ----------
        cart : Cart
            保存するカートエンティティ。
        """
        self._carts[cart.user_id] = cart

    def delete(self, user_id: str) -> None:
        """
        ユーザーIDを指定してカートを削除する.

        Parameters
        ----------
        user_id : str
            削除対象のユーザーID。
        """
        self._carts.pop(user_id, None)
