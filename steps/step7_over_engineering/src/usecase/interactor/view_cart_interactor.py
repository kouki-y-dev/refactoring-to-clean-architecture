"""カート表示ユースケースの実装 (Interactor) ."""

from typing import TYPE_CHECKING

from domain.entity import TAX_RATE

from usecase.port.view_cart_port import (
    CartDetailItemDTO,
    ViewCartInputPort,
    ViewCartResponseDTO,
)

if TYPE_CHECKING:
    from domain.gateway import ICartGateway, IProductGateway

    from usecase.port.view_cart_port import (
        ViewCartOutputPort,
        ViewCartRequestDTO,
    )


class ViewCartInteractor(ViewCartInputPort):
    """カート表示インターラクター (ユースケース実装).

    Parameters
    ----------
    cart_gateway : ICartGateway
        カートデータアクセスゲートウェイ。
    product_gateway : IProductGateway
        商品データアクセスゲートウェイ。
    output_port : ViewCartOutputPort
        出力境界インターフェース。
    """

    def __init__(
        self,
        cart_gateway: ICartGateway,
        product_gateway: IProductGateway,
        output_port: ViewCartOutputPort,
    ) -> None:
        self.cart_gateway = cart_gateway
        self.product_gateway = product_gateway
        self.output_port = output_port

    def execute(self, request: ViewCartRequestDTO) -> None:
        """カート内容を集計し、OutputPort へ通知する.

        Parameters
        ----------
        request : ViewCartRequestDTO
            リクエストデータ。
        """
        cart = self.cart_gateway.find_by_user_id(request.user_id)
        if cart is None or cart.is_empty:
            response = ViewCartResponseDTO(
                is_empty=True,
                user_id=request.user_id,
                items=[],
                subtotal=0,
                tax=0,
                total=0,
            )
            self.output_port.present_success(response)
            return

        items: list[CartDetailItemDTO] = []
        for item in cart.items:
            product = self.product_gateway.find_by_id(item.product_id)
            if product is None:
                continue

            item_total = product.price * item.quantity
            items.append(
                CartDetailItemDTO(
                    product_id=product.id,
                    name=product.name,
                    price=product.price,
                    quantity=item.quantity,
                    item_total=item_total,
                )
            )

        subtotal = sum(i.item_total for i in items)
        tax = int(subtotal * TAX_RATE)
        total = subtotal + tax

        response = ViewCartResponseDTO(
            is_empty=False,
            user_id=request.user_id,
            items=items,
            subtotal=subtotal,
            tax=tax,
            total=total,
        )
        self.output_port.present_success(response)
