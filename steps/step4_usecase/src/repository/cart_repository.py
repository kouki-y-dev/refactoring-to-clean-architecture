"""カートリポジトリモジュール.

Cart エンティティのデータアクセス・永続化をコレクションのように扱います。
"""

from domain.entity import Cart


class CartRepository:
    """カートリポジトリ.

    Parameters
    ----------
    carts : dict[str, Cart] | None, optional
        初期カートデータ。省略時は空の辞書を使用。
    """

    def __init__(self, carts: dict[str, Cart] | None = None) -> None:
        self._carts: dict[str, Cart] = carts if carts is not None else {}

    def find_by_user_id(self, user_id: str) -> Cart | None:
        """ユーザーIDに紐づくカートを取得する.

        Parameters
        ----------
        user_id : str
            ユーザーID。

        Returns
        -------
        Cart | None
            カートエンティティ。存在しない場合は None。
        """
        return self._carts.get(user_id)

    def get_or_create(self, user_id: str) -> Cart:
        """ユーザーIDに紐づくカートを取得し、存在しない場合は新規作成する.

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
            cart = Cart(user_id=user_id)
            self.save(cart)
        return cart

    def save(self, cart: Cart) -> None:
        """カートを保存・更新する.

        Parameters
        ----------
        cart : Cart
            保存するカートエンティティ。
        """
        self._carts[cart.user_id] = cart

    def delete(self, user_id: str) -> None:
        """ユーザーのカートを削除する.

        Parameters
        ----------
        user_id : str
            削除対象のユーザーID。
        """
        self._carts.pop(user_id, None)
