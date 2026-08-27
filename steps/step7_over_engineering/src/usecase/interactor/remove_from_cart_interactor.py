"""カート削除ユースケースの実装 (Interactor) ."""

from typing import TYPE_CHECKING

from usecase.port.remove_from_cart_port import (
    RemoveFromCartInputPort,
    RemoveFromCartResponseDTO,
)

if TYPE_CHECKING:
    from domain.gateway import ICartGateway

    from usecase.port.remove_from_cart_port import (
        RemoveFromCartOutputPort,
        RemoveFromCartRequestDTO,
    )


class RemoveFromCartInteractor(RemoveFromCartInputPort):
    """カート削除インターラクター (ユースケース実装).

    Parameters
    ----------
    cart_gateway : ICartGateway
        カートデータアクセスゲートウェイ。
    output_port : RemoveFromCartOutputPort
        出力境界インターフェース。
    """

    def __init__(
        self,
        cart_gateway: ICartGateway,
        output_port: RemoveFromCartOutputPort,
    ) -> None:
        self.cart_gateway = cart_gateway
        self.output_port = output_port

    def execute(self, request: RemoveFromCartRequestDTO) -> None:
        """カートから商品を削除し、OutputPort へ通知する.

        Parameters
        ----------
        request : RemoveFromCartRequestDTO
            リクエストデータ。
        """
        cart = self.cart_gateway.find_by_user_id(request.user_id)
        if cart is None:
            self.output_port.present_error(
                f"エラー: 商品 {request.product_id} はカートにありません"
            )
            return

        try:
            cart.remove_item(request.product_id)
        except ValueError as e:
            self.output_port.present_error(str(e))
            return

        self.cart_gateway.save(cart)
        response = RemoveFromCartResponseDTO(product_id=request.product_id)
        self.output_port.present_success(response)
