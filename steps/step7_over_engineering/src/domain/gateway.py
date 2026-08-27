"""ドメイン層のゲートウェイ (リポジトリ) インターフェース定義.

クリーンアーキテクチャの原典に従い、エンティティの永続化およびデータアクセスを行う
境界インターフェース (Gateway / Repository Interface) を定義します。
ドメイン層・ユースケース層はこれら抽象インターフェースに依存し、具象実装の詳細を知りません。
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.entity import Cart, Order, Product


class IProductGateway(ABC):
    """商品データアクセスゲートウェイの抽象インターフェース."""

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

    @abstractmethod
    def save(self, product: Product) -> None:
        """商品情報を保存・更新する.

        Parameters
        ----------
        product : Product
            保存する商品エンティティ。
        """


class ICartGateway(ABC):
    """カートデータアクセスゲートウェイの抽象インターフェース."""

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
    def save(self, cart: Cart) -> None:
        """カート情報を保存・更新する.

        Parameters
        ----------
        cart : Cart
            保存するカートエンティティ。
        """


class IOrderGateway(ABC):
    """注文データアクセスゲートウェイの抽象インターフェース."""

    @abstractmethod
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

    @abstractmethod
    def save(self, order: Order) -> None:
        """注文情報を保存する.

        Parameters
        ----------
        order : Order
            保存する注文エンティティ。
        """

    @abstractmethod
    def next_order_id(self) -> str:
        """新しい注文IDを採番する.

        Returns
        -------
        str
            一意の注文ID文字列。
        """
