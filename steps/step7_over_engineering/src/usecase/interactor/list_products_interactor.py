"""商品一覧取得ユースケースの実装 (Interactor) ."""

from typing import TYPE_CHECKING

from usecase.port.list_products_port import (
    ListProductsInputPort,
    ListProductsResponseDTO,
    ProductItemDTO,
)

if TYPE_CHECKING:
    from domain.gateway import IProductGateway

    from usecase.port.list_products_port import (
        ListProductsOutputPort,
        ListProductsRequestDTO,
    )


class ListProductsInteractor(ListProductsInputPort):
    """商品一覧取得インターラクター (ユースケース実装).

    Parameters
    ----------
    product_gateway : IProductGateway
        商品データアクセスゲートウェイ。
    output_port : ListProductsOutputPort
        出力境界インターフェース。
    """

    def __init__(
        self,
        product_gateway: IProductGateway,
        output_port: ListProductsOutputPort,
    ) -> None:
        self.product_gateway = product_gateway
        self.output_port = output_port

    def execute(self, request: ListProductsRequestDTO) -> None:
        """商品一覧を取得し、OutputPort へ通知する.

        Parameters
        ----------
        request : ListProductsRequestDTO
            リクエストデータ。
        """
        _ = request
        products = self.product_gateway.find_all()
        items = [
            ProductItemDTO(
                product_id=p.id,
                name=p.name,
                price=p.price,
                stock=p.stock,
            )
            for p in products
        ]
        response = ListProductsResponseDTO(products=items)
        self.output_port.present_success(response)
