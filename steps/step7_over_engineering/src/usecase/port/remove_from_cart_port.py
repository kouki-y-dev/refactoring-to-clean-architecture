"""カート削除ユースケースの Port (Boundary) 定義.

Clean Architecture の Input Port / Output Port /
Request DTO / Response DTO を定義します。
"""

from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict


class RemoveFromCartRequestDTO(BaseModel):
    """カート削除リクエスト DTO.

    Attributes
    ----------
    user_id : str
        ユーザーID。
    product_id : str
        削除対象の商品ID。
    """

    user_id: str
    product_id: str

    model_config = ConfigDict(frozen=True)


class RemoveFromCartResponseDTO(BaseModel):
    """カート削除レスポンス DTO.

    Attributes
    ----------
    product_id : str
        削除された商品ID。
    """

    product_id: str

    model_config = ConfigDict(frozen=True)


class RemoveFromCartInputPort(ABC):
    """カート削除ユースケースの入力境界 (Input Port) インターフェース."""

    @abstractmethod
    def execute(self, request: RemoveFromCartRequestDTO) -> None:
        """カート削除ユースケースを実行する.

        Parameters
        ----------
        request : RemoveFromCartRequestDTO
            カート削除リクエストデータ。
        """


class RemoveFromCartOutputPort(ABC):
    """カート削除ユースケースの出力境界 (Output Port) インターフェース."""

    @abstractmethod
    def present_success(self, response: RemoveFromCartResponseDTO) -> None:
        """処理成功時の結果を出力境界へ通知する.

        Parameters
        ----------
        response : RemoveFromCartResponseDTO
            カート削除レスポンスデータ。
        """

    @abstractmethod
    def present_error(self, error_message: str) -> None:
        """処理失敗時のエラーメッセージを出力境界へ通知する.

        Parameters
        ----------
        error_message : str
            エラーメッセージ。
        """
