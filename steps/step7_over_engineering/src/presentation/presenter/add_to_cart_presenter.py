"""カート追加プレゼンターの実装."""

from usecase.port.add_to_cart_port import (
    AddToCartOutputPort,
    AddToCartResponseDTO,
)

from presentation.view_model.models import AddToCartViewModel


class AddToCartPresenter(AddToCartOutputPort):
    """カート追加出力境界の実装プレゼンター."""

    def __init__(self) -> None:
        self.view_model: AddToCartViewModel = AddToCartViewModel()

    def present_success(self, response: AddToCartResponseDTO) -> None:
        """成功結果を ViewModel に変換・設定する.

        Parameters
        ----------
        response : AddToCartResponseDTO
            レスポンス DTO。
        """
        self.view_model = AddToCartViewModel(
            is_success=True,
            message=f"カートに追加/更新しました: {response.product_name}",
        )

    def present_error(self, error_message: str) -> None:
        """エラー結果を ViewModel に設定する.

        Parameters
        ----------
        error_message : str
            エラーメッセージ。
        """
        self.view_model = AddToCartViewModel(
            is_success=False,
            error_message=error_message,
        )
