"""注文確定プレゼンターの実装."""

from usecase.port.place_order_port import (
    PlaceOrderOutputPort,
    PlaceOrderResponseDTO,
)

from presentation.view_model.models import PlaceOrderViewModel


class PlaceOrderPresenter(PlaceOrderOutputPort):
    """注文確定出力境界の実装プレゼンター."""

    def __init__(self) -> None:
        self.view_model: PlaceOrderViewModel = PlaceOrderViewModel()

    def present_success(self, response: PlaceOrderResponseDTO) -> None:
        """成功結果を ViewModel に変換・設定する.

        Parameters
        ----------
        response : PlaceOrderResponseDTO
            レスポンス DTO。
        """
        self.view_model = PlaceOrderViewModel(
            is_success=True,
            order_id=response.order_id,
            total_display=f"¥{response.total}",
        )

    def present_error(self, error_message: str) -> None:
        """エラー結果を ViewModel に設定する.

        Parameters
        ----------
        error_message : str
            エラーメッセージ。
        """
        self.view_model = PlaceOrderViewModel(
            is_success=False,
            error_message=error_message,
        )
