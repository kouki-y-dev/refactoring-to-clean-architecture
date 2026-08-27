"""商品一覧取得ユースケースの Port (Boundary) 定義.

Clean Architecture の Input Port / Output Port /
Request DTO / Response DTO を定義します。
"""

from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict, Field


class ListProductsRequestDTO(BaseModel):
    """商品一覧取得リクエスト DTO."""

    model_config = ConfigDict(frozen=True)


class ProductItemDTO(BaseModel):
    """商品情報 DTO.

    Attributes
    ----------
    product_id : str
        商品ID。
    name : str
        商品名。
    price : int
        価格。
    stock : int
        在庫数。
    """

    product_id: str
    name: str
    price: int = Field(ge=0)
    stock: int = Field(ge=0)

    model_config = ConfigDict(frozen=True)


class ListProductsResponseDTO(BaseModel):
    """商品一覧取得レスポンス DTO.

    Attributes
    ----------
    products : list[ProductItemDTO]
        商品一覧リスト。
    """

    products: list[ProductItemDTO]

    model_config = ConfigDict(frozen=True)


class ListProductsInputPort(ABC):
    """商品一覧取得ユースケースの入力境界 (Input Port) インターフェース."""

    @abstractmethod
    def execute(self, request: ListProductsRequestDTO) -> None:
        """商品一覧取得ユースケースを実行する.

        Parameters
        ----------
        request : ListProductsRequestDTO
            商品一覧取得リクエストデータ。
        """


class ListProductsOutputPort(ABC):
    """商品一覧取得ユースケースの出力境界 (Output Port) インターフェース."""

    @abstractmethod
    def present_success(self, response: ListProductsResponseDTO) -> None:
        """処理成功時の結果を出力境界へ通知する.

        Parameters
        ----------
        response : ListProductsResponseDTO
            商品一覧取得レスポンスデータ。
        """

    @abstractmethod
    def present_error(self, error_message: str) -> None:
        """処理失敗時のエラーメッセージを出力境界へ通知する.

        Parameters
        ----------
        error_message : str
            エラーメッセージ。
        """
