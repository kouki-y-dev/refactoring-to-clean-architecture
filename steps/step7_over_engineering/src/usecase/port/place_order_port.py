"""注文確定ユースケースの Port (Boundary) 定義.

Clean Architecture の Input Port / Output Port /
Request DTO / Response DTO を定義します。
"""

from abc import ABC, abstractmethod
from datetime import datetime  # noqa: TC003

from pydantic import BaseModel, ConfigDict, Field


class PlaceOrderRequestDTO(BaseModel):
    """注文確定リクエスト DTO.

    Attributes
    ----------
    user_id : str
        ユーザーID。
    """

    user_id: str

    model_config = ConfigDict(frozen=True)


class OrderItemDTO(BaseModel):
    """注文明細 DTO.

    Attributes
    ----------
    product_id : str
        商品ID。
    name : str
        商品名。
    price : int
        単価。
    quantity : int
        数量。
    subtotal : int
        小計。
    """

    product_id: str
    name: str
    price: int = Field(ge=0)
    quantity: int = Field(gt=0)
    subtotal: int = Field(ge=0)

    model_config = ConfigDict(frozen=True)


class PlaceOrderResponseDTO(BaseModel):
    """注文確定レスポンス DTO.

    Attributes
    ----------
    order_id : str
        注文ID。
    user_id : str
        ユーザーID。
    items : list[OrderItemDTO]
        注文明細リスト。
    subtotal : int
        小計 (税抜) 。
    tax : int
        消費税額。
    total : int
        合計金額 (税込) 。
    created_at : datetime
        注文作成日時。
    """

    order_id: str
    user_id: str
    items: list[OrderItemDTO]
    subtotal: int = Field(ge=0)
    tax: int = Field(ge=0)
    total: int = Field(ge=0)
    created_at: datetime

    model_config = ConfigDict(frozen=True)


class PlaceOrderInputPort(ABC):
    """注文確定ユースケースの入力境界 (Input Port) インターフェース."""

    @abstractmethod
    def execute(self, request: PlaceOrderRequestDTO) -> None:
        """注文確定ユースケースを実行する.

        Parameters
        ----------
        request : PlaceOrderRequestDTO
            注文確定リクエストデータ。
        """


class PlaceOrderOutputPort(ABC):
    """注文確定ユースケースの出力境界 (Output Port) インターフェース."""

    @abstractmethod
    def present_success(self, response: PlaceOrderResponseDTO) -> None:
        """処理成功時の結果を出力境界へ通知する.

        Parameters
        ----------
        response : PlaceOrderResponseDTO
            注文確定レスポンスデータ。
        """

    @abstractmethod
    def present_error(self, error_message: str) -> None:
        """処理失敗時のエラーメッセージを出力境界へ通知する.

        Parameters
        ----------
        error_message : str
            エラーメッセージ。
        """
