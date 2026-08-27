"""カート追加ユースケースの実装 (Interactor) ."""

from typing import TYPE_CHECKING

from usecase.port.add_to_cart_port import (
    AddToCartInputPort,
    AddToCartResponseDTO,
)

if TYPE_CHECKING:
    from domain.gateway import ICartGateway, IProductGateway

    from usecase.port.add_to_cart_port import (
        AddToCartOutputPort,
        AddToCartRequestDTO,
    )


class AddToCartInteractor(AddToCartInputPort):
    """カート追加インターラクター (ユースケース実装).

    Parameters
    ----------
    product_gateway : IProductGateway
        商品データアクセスゲートウェイ。
    cart_gateway : ICartGateway
        カートデータアクセスゲートウェイ。
    output_port : AddToCartOutputPort
        出力境界インターフェース。
    """

    def __init__(
        self,
        product_gateway: IProductGateway,
        cart_gateway: ICartGateway,
        output_port: AddToCartOutputPort,
    ) -> None:
        self.product_gateway = product_gateway
        self.cart_gateway = cart_gateway
        self.output_port = output_port

    def execute(self, request: AddToCartRequestDTO) -> None:
        """商品をカートに追加し、OutputPort へ通知する.

        Parameters
        ----------
        request : AddToCartRequestDTO
            リクエストデータ。
        """
        product = self.product_gateway.find_by_id(request.product_id)
        if product is None:
            self.output_port.present_error(
                f"エラー: 商品 {request.product_id} が見つかりません"
            )
            return

        if not product.has_enough_stock(request.quantity):
            self.output_port.present_error(
                f"エラー: {product.name} の在庫が不足しています"
                f"(残り {product.stock}個)"
            )
            return

        cart = self.cart_gateway.get_or_create(request.user_id)
        cart.add_item(request.product_id, request.quantity)
        self.cart_gateway.save(cart)

        response = AddToCartResponseDTO(
            product_id=product.id,
            product_name=product.name,
            price=product.price,
            quantity=request.quantity,
            stock=product.stock,
        )
        self.output_port.present_success(response)
