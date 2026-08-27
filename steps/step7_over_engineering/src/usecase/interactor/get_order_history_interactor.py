"""注文履歴取得ユースケースの実装 (Interactor) ."""

from typing import TYPE_CHECKING

from usecase.port.get_order_history_port import (
    GetOrderHistoryInputPort,
    GetOrderHistoryResponseDTO,
    OrderHistoryItemDTO,
)
from usecase.port.place_order_port import OrderItemDTO

if TYPE_CHECKING:
    from domain.gateway import IOrderGateway

    from usecase.port.get_order_history_port import (
        GetOrderHistoryOutputPort,
        GetOrderHistoryRequestDTO,
    )


class GetOrderHistoryInteractor(GetOrderHistoryInputPort):
    """注文履歴取得インターラクター (ユースケース実装).

    Parameters
    ----------
    order_gateway : IOrderGateway
        注文データアクセスゲートウェイ。
    output_port : GetOrderHistoryOutputPort
        出力境界インターフェース。
    """

    def __init__(
        self,
        order_gateway: IOrderGateway,
        output_port: GetOrderHistoryOutputPort,
    ) -> None:
        self.order_gateway = order_gateway
        self.output_port = output_port

    def execute(self, request: GetOrderHistoryRequestDTO) -> None:
        """注文履歴を取得し、OutputPort へ通知する.

        Parameters
        ----------
        request : GetOrderHistoryRequestDTO
            リクエストデータ。
        """
        orders = self.order_gateway.find_by_user_id(request.user_id)
        history_dtos = [
            OrderHistoryItemDTO(
                order_id=order.order_id,
                user_id=order.user_id,
                items=[
                    OrderItemDTO(
                        product_id=item.product_id,
                        name=item.name,
                        price=item.price,
                        quantity=item.quantity,
                        subtotal=item.subtotal,
                    )
                    for item in order.items
                ],
                subtotal=order.subtotal,
                tax=order.tax,
                total=order.total,
                created_at=order.created_at,
            )
            for order in orders
        ]
        response = GetOrderHistoryResponseDTO(orders=history_dtos)
        self.output_port.present_success(response)
