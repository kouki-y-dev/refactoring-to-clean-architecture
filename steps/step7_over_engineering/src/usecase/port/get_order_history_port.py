"""注文履歴取得ユースケースの Port (Boundary) 定義.

Clean Architecture の Input Port / Output Port /
Request DTO / Response DTO を定義します。
"""

from abc import ABC, abstractmethod
from datetime import datetime  # noqa: TC003

from pydantic import BaseModel, ConfigDict, Field

from usecase.port.place_order_port import OrderItemDTO  # noqa: TC001


class GetOrderHistoryRequestDTO(BaseModel):
    """注文履歴取得リクエスト DTO.

    Attributes
    ----------
    user_id : str
        ユーザーID。
    """

    user_id: str

    model_config = ConfigDict(frozen=True)


class OrderHistoryItemDTO(BaseModel):
    """注文履歴用明細 DTO.

    Attributes
    ----------
    order_id : str
        注文ID。
    user_id : str
        ユーザーID。
    items : list[OrderItemDTO]
        明細リスト。
    subtotal : int
        小計 (税抜) 。
    tax : int
        消費税額。
    total : int
        合計金額 (税込) 。
    created_at : datetime
        注文日時。
    """

    order_id: str
    user_id: str
    items: list[OrderItemDTO]
    subtotal: int = Field(ge=0)
    tax: int = Field(ge=0)
    total: int = Field(ge=0)
    created_at: datetime

    model_config = ConfigDict(frozen=True)


class GetOrderHistoryResponseDTO(BaseModel):
    """注文履歴取得レスポンス DTO.

    Attributes
    ----------
    orders : list[OrderHistoryItemDTO]
        注文履歴リスト。
    """

    orders: list[OrderHistoryItemDTO]

    model_config = ConfigDict(frozen=True)


class GetOrderHistoryInputPort(ABC):
    """注文履歴取得ユースケースの入力境界 (Input Port) インターフェース."""

    @abstractmethod
    def execute(self, request: GetOrderHistoryRequestDTO) -> None:
        """注文履歴取得ユースケースを実行する.

        Parameters
        ----------
        request : GetOrderHistoryRequestDTO
            注文履歴取得リクエストデータ。
        """


class GetOrderHistoryOutputPort(ABC):
    """注文履歴取得ユースケースの出力境界 (Output Port) インターフェース."""

    @abstractmethod
    def present_success(self, response: GetOrderHistoryResponseDTO) -> None:
        """処理成功時の結果を出力境界へ通知する.

        Parameters
        ----------
        response : GetOrderHistoryResponseDTO
            注文履歴取得レスポンスデータ。
        """

    @abstractmethod
    def present_error(self, error_message: str) -> None:
        """処理失敗時のエラーメッセージを出力境界へ通知する.

        Parameters
        ----------
        error_message : str
            エラーメッセージ。
        """
