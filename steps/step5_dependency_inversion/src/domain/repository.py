"""リポジトリインターフェースモジュール.

ドメイン層・ユースケース層が利用する
リポジトリの抽象基底クラス (Interface) を定義します。
依存関係逆転の原則 (DIP) に従い、
高水準モジュール (ユースケース層) は
低水準モジュール (データアクセス具象実装) ではなく、
この抽象インターフェースに依存します。
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.entity import Cart, Order, Product


class IProductRepository(ABC):
    """商品リポジトリのインターフェース."""

    @abstractmethod
    def find_all(self) -> list[Product]:
        """全商品を取得する.

        Returns
        -------
        list[Product]
            商品エンティティのリスト。
        """

    @abstractmethod
    def find_by_id(self, product_id: str) -> Product | None:
        """商品IDによって商品を検索する.

        Parameters
        ----------
        product_id : str
            検索する商品ID。

        Returns
        -------
        Product | None
            商品エンティティ。存在しない場合は None。
        """

    @abstractmethod
    def save(self, product: Product) -> None:
        """商品を保存・更新する.

        Parameters
        ----------
        product : Product
            保存する商品エンティティ。
        """


class ICartRepository(ABC):
    """カートリポジトリのインターフェース."""

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
    def save(self, cart: Cart) -> None:
        """カートを保存・更新する.

        Parameters
        ----------
        cart : Cart
            保存するカートエンティティ。
        """

    @abstractmethod
    def delete(self, user_id: str) -> None:
        """ユーザーのカートを削除する.

        Parameters
        ----------
        user_id : str
            削除対象のユーザーID。
        """


class IOrderRepository(ABC):
    """注文リポジトリのインターフェース."""

    @abstractmethod
    def save(self, order: Order) -> None:
        """注文を保存する.

        Parameters
        ----------
        order : Order
            保存する注文エンティティ。
        """

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
    def find_all(self) -> list[Order]:
        """全注文を取得する.

        Returns
        -------
        list[Order]
            全注文エンティティのリスト。
        """

    @abstractmethod
    def count(self) -> int:
        """保存されている注文の総数を返す.

        Returns
        -------
        int
            注文総数。
        """

    @abstractmethod
    def next_order_id(self) -> str:
        """新しい注文IDを採番する.

        Returns
        -------
        str
            新規注文ID (例: 'ORD-0001') 。
        """
