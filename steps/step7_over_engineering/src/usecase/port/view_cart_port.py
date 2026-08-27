"""カート表示ユースケースの Port (Boundary) 定義.

Clean Architecture の Input Port / Output Port /
Request DTO / Response DTO を定義します。
"""

from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict, Field


class ViewCartRequestDTO(BaseModel):
    """カート表示リクエスト DTO.

    Attributes
    ----------
    user_id : str
        ユーザーID。
    """

    user_id: str

    model_config = ConfigDict(frozen=True)


class CartDetailItemDTO(BaseModel):
    """カート内商品明細 DTO.

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
    item_total : int
        小計。
    """

    product_id: str
    name: str
    price: int = Field(ge=0)
    quantity: int = Field(gt=0)
    item_total: int = Field(ge=0)

    model_config = ConfigDict(frozen=True)


class ViewCartResponseDTO(BaseModel):
    """カート表示レスポンス DTO.

    Attributes
    ----------
    is_empty : bool
        カートが空かどうか。
    user_id : str
        ユーザーID。
    items : list[CartDetailItemDTO]
        明細リスト。
    subtotal : int
        小計 (税抜) 。
    tax : int
        消費税額。
    total : int
        合計金額 (税込) 。
    """

    is_empty: bool
    user_id: str
    items: list[CartDetailItemDTO] = Field(default_factory=list)
    subtotal: int = Field(default=0, ge=0)
    tax: int = Field(default=0, ge=0)
    total: int = Field(default=0, ge=0)

    model_config = ConfigDict(frozen=True)


class ViewCartInputPort(ABC):
    """カート表示ユースケースの入力境界 (Input Port) インターフェース."""

    @abstractmethod
    def execute(self, request: ViewCartRequestDTO) -> None:
        """カート表示ユースケースを実行する.

        Parameters
        ----------
        request : ViewCartRequestDTO
            カート表示リクエストデータ。
        """


class ViewCartOutputPort(ABC):
    """カート表示ユースケースの出力境界 (Output Port) インターフェース."""

    @abstractmethod
    def present_success(self, response: ViewCartResponseDTO) -> None:
        """処理成功時の結果を出力境界へ通知する.

        Parameters
        ----------
        response : ViewCartResponseDTO
            カート表示レスポンスデータ。
        """

    @abstractmethod
    def present_error(self, error_message: str) -> None:
        """処理失敗時のエラーメッセージを出力境界へ通知する.

        Parameters
        ----------
        error_message : str
            エラーメッセージ。
        """
