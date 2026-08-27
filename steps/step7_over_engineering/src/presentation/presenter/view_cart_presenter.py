"""カート表示プレゼンターの実装."""

from usecase.port.view_cart_port import (
    ViewCartOutputPort,
    ViewCartResponseDTO,
)

from presentation.view_model.models import (
    ViewCartItemViewModel,
    ViewCartViewModel,
)


class ViewCartPresenter(ViewCartOutputPort):
    """カート表示出力境界の実装プレゼンター."""

    def __init__(self) -> None:
        self.view_model: ViewCartViewModel = ViewCartViewModel()

    def present_success(self, response: ViewCartResponseDTO) -> None:
        """成功結果を ViewModel に変換・設定する.

        Parameters
        ----------
        response : ViewCartResponseDTO
            レスポンス DTO。
        """
        if response.is_empty:
            self.view_model = ViewCartViewModel(
                is_success=True,
                is_empty=True,
                user_id=response.user_id,
            )
            return

        items = [
            ViewCartItemViewModel(
                name=item.name,
                quantity_display=str(item.quantity),
                total_display=f"¥{item.item_total}",
            )
            for item in response.items
        ]
        self.view_model = ViewCartViewModel(
            is_success=True,
            is_empty=False,
            user_id=response.user_id,
            items=items,
            subtotal_display=f"¥{response.subtotal}",
            tax_display=f"¥{response.tax}",
            total_display=f"¥{response.total}",
        )

    def present_error(self, error_message: str) -> None:
        """エラー結果を ViewModel に設定する.

        Parameters
        ----------
        error_message : str
            エラーメッセージ。
        """
        self.view_model = ViewCartViewModel(
            is_success=False,
            error_message=error_message,
        )
