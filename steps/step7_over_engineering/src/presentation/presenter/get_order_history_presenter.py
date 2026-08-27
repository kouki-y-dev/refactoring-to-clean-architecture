"""注文履歴取得プレゼンターの実装."""

from usecase.port.get_order_history_port import (
    GetOrderHistoryOutputPort,
    GetOrderHistoryResponseDTO,
)

from presentation.view_model.models import (
    GetOrderHistoryViewModel,
    OrderHistoryItemViewModel,
    PlaceOrderItemViewModel,
)


class GetOrderHistoryPresenter(GetOrderHistoryOutputPort):
    """注文履歴出力境界の実装プレゼンター."""

    def __init__(self) -> None:
        self.view_model: GetOrderHistoryViewModel = GetOrderHistoryViewModel()

    def present_success(self, response: GetOrderHistoryResponseDTO) -> None:
        """成功結果を ViewModel に変換・設定する.

        Parameters
        ----------
        response : GetOrderHistoryResponseDTO
            レスポンス DTO。
        """
        history_items = [
            OrderHistoryItemViewModel(
                order_id=order.order_id,
                created_at_display=str(order.created_at),
                total_display=f"¥{order.total}",
                items=[
                    PlaceOrderItemViewModel(
                        name=item.name,
                        quantity=item.quantity,
                        subtotal_display=f"¥{item.subtotal}",
                    )
                    for item in order.items
                ],
            )
            for order in response.orders
        ]
        self.view_model = GetOrderHistoryViewModel(
            is_success=True,
            orders=history_items,
        )

    def present_error(self, error_message: str) -> None:
        """エラー結果を ViewModel に設定する.

        Parameters
        ----------
        error_message : str
            エラーメッセージ。
        """
        self.view_model = GetOrderHistoryViewModel(
            is_success=False,
            error_message=error_message,
        )
