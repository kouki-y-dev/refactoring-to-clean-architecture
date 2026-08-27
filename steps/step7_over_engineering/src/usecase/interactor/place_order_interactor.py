"""注文確定ユースケースの実装 (Interactor) ."""

from typing import TYPE_CHECKING

from domain.entity import Order, OrderItem

from usecase.port.place_order_port import (
    OrderItemDTO,
    PlaceOrderInputPort,
    PlaceOrderResponseDTO,
)

if TYPE_CHECKING:
    from domain.gateway import ICartGateway, IOrderGateway, IProductGateway

    from usecase.port.place_order_port import (
        PlaceOrderOutputPort,
        PlaceOrderRequestDTO,
    )


class PlaceOrderInteractor(PlaceOrderInputPort):
    """注文確定インターラクター (ユースケース実装).

    Parameters
    ----------
    cart_gateway : ICartGateway
        カートデータアクセスゲートウェイ。
    product_gateway : IProductGateway
        商品データアクセスゲートウェイ。
    order_gateway : IOrderGateway
        注文データアクセスゲートウェイ。
    output_port : PlaceOrderOutputPort
        出力境界インターフェース。
    """

    def __init__(
        self,
        cart_gateway: ICartGateway,
        product_gateway: IProductGateway,
        order_gateway: IOrderGateway,
        output_port: PlaceOrderOutputPort,
    ) -> None:
        self.cart_gateway = cart_gateway
        self.product_gateway = product_gateway
        self.order_gateway = order_gateway
        self.output_port = output_port

    def execute(self, request: PlaceOrderRequestDTO) -> None:
        """注文確定処理を実行し、OutputPort へ通知する.

        Parameters
        ----------
        request : PlaceOrderRequestDTO
            リクエストデータ。
        """
        cart = self.cart_gateway.find_by_user_id(request.user_id)
        if cart is None or cart.is_empty:
            self.output_port.present_error("エラー: カートが空です")
            return

        # 1. 在庫チェック
        for cart_item in cart.items:
            product = self.product_gateway.find_by_id(cart_item.product_id)
            if product is None:
                self.output_port.present_error(
                    f"エラー: 商品 {cart_item.product_id} が見つかりません"
                )
                return

            if not product.has_enough_stock(cart_item.quantity):
                self.output_port.present_error(
                    f"エラー: {product.name} の在庫が不足しています"
                    f"(残り {product.stock}個)"
                )
                return

        # 2. 注文明細アイテムの作成
        order_items: list[OrderItem] = []
        for cart_item in cart.items:
            product = self.product_gateway.find_by_id(cart_item.product_id)
            if product is None:
                continue

            item_total = product.price * cart_item.quantity
            order_items.append(
                OrderItem(
                    product_id=cart_item.product_id,
                    name=product.name,
                    price=product.price,
                    quantity=cart_item.quantity,
                    subtotal=item_total,
                )
            )

        # 3. 注文エンティティ作成と永続化
        order_id = self.order_gateway.next_order_id()
        order = Order.create(
            order_id=order_id,
            user_id=request.user_id,
            items=order_items,
        )
        self.order_gateway.save(order)

        # 4. 在庫減少と永続化
        for cart_item in cart.items:
            product = self.product_gateway.find_by_id(cart_item.product_id)
            if product is not None:
                product.decrease_stock(cart_item.quantity)
                self.product_gateway.save(product)

        # 5. カートクリアと永続化
        cart.clear()
        self.cart_gateway.save(cart)

        # 6. レスポンス DTO への変換と OutputPort 呼び出し
        dto_items = [
            OrderItemDTO(
                product_id=item.product_id,
                name=item.name,
                price=item.price,
                quantity=item.quantity,
                subtotal=item.subtotal,
            )
            for item in order.items
        ]
        response = PlaceOrderResponseDTO(
            order_id=order.order_id,
            user_id=order.user_id,
            items=dto_items,
            subtotal=order.subtotal,
            tax=order.tax,
            total=order.total,
            created_at=order.created_at,
        )
        self.output_port.present_success(response)
