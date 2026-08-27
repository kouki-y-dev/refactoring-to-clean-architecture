"""カート追加ユースケースの Port (Boundary) 定義.

Clean Architecture の Input Port / Output Port /
Request DTO / Response DTO を定義します。
"""

from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict, Field


class AddToCartRequestDTO(BaseModel):
    """カート追加リクエスト DTO.

    Attributes
    ----------
    user_id : str
        ユーザーID。
    product_id : str
        商品ID。
    quantity : int
        追加数量。
    """

    user_id: str
    product_id: str
    quantity: int = Field(gt=0)

    model_config = ConfigDict(frozen=True)


class AddToCartResponseDTO(BaseModel):
    """カート追加レスポンス DTO.

    Attributes
    ----------
    product_id : str
        追加された商品ID。
    product_name : str
        追加された商品名。
    price : int
        商品単価。
    quantity : int
        追加された数量。
    stock : int
        現在の残り在庫数。
    """

    product_id: str
    product_name: str
    price: int = Field(ge=0)
    quantity: int = Field(gt=0)
    stock: int = Field(ge=0)

    model_config = ConfigDict(frozen=True)


class AddToCartInputPort(ABC):
    """カート追加ユースケースの入力境界 (Input Port) インターフェース."""

    @abstractmethod
    def execute(self, request: AddToCartRequestDTO) -> None:
        """カート追加ユースケースを実行する.

        Parameters
        ----------
        request : AddToCartRequestDTO
            カート追加リクエストデータ。
        """


class AddToCartOutputPort(ABC):
    """カート追加ユースケースの出力境界 (Output Port) インターフェース."""

    @abstractmethod
    def present_success(self, response: AddToCartResponseDTO) -> None:
        """処理成功時の結果を出力境界へ通知する.

        Parameters
        ----------
        response : AddToCartResponseDTO
            カート追加レスポンスデータ。
        """

    @abstractmethod
    def present_error(self, error_message: str) -> None:
        """処理失敗時のエラーメッセージを出力境界へ通知する.

        Parameters
        ----------
        error_message : str
            エラーメッセージ。
        """
