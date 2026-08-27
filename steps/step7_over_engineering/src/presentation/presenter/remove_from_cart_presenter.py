"""カート削除プレゼンターの実装."""

from usecase.port.remove_from_cart_port import (
    RemoveFromCartOutputPort,
    RemoveFromCartResponseDTO,
)

from presentation.view_model.models import RemoveFromCartViewModel


class RemoveFromCartPresenter(RemoveFromCartOutputPort):
    """カート削除出力境界の実装プレゼンター."""

    def __init__(self) -> None:
        self.view_model: RemoveFromCartViewModel = RemoveFromCartViewModel()

    def present_success(self, response: RemoveFromCartResponseDTO) -> None:
        """成功結果を ViewModel に変換・設定する.

        Parameters
        ----------
        response : RemoveFromCartResponseDTO
            レスポンス DTO。
        """
        self.view_model = RemoveFromCartViewModel(
            is_success=True,
            message=f"カートから削除しました: {response.product_id}",
        )

    def present_error(self, error_message: str) -> None:
        """エラー結果を ViewModel に設定する.

        Parameters
        ----------
        error_message : str
            エラーメッセージ。
        """
        self.view_model = RemoveFromCartViewModel(
            is_success=False,
            error_message=error_message,
        )
