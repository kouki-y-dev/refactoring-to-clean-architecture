"""プレゼンテーション層のコントローラー (Controller) モジュール.

UI からの入力を受け取り、各ユースケースの Request DTO を組み立てて
対応する Input Port を実行します。
コントローラー自体はドメインエンティティやプレゼンターの内部実装には依存せず、
Input Port と Request DTO のみに依存します。
"""

from typing import TYPE_CHECKING

from usecase.port.add_to_cart_port import AddToCartRequestDTO
from usecase.port.get_order_history_port import GetOrderHistoryRequestDTO
from usecase.port.list_products_port import ListProductsRequestDTO
from usecase.port.place_order_port import PlaceOrderRequestDTO
from usecase.port.remove_from_cart_port import RemoveFromCartRequestDTO
from usecase.port.view_cart_port import ViewCartRequestDTO

if TYPE_CHECKING:
    from usecase.port.add_to_cart_port import AddToCartInputPort
    from usecase.port.get_order_history_port import (
        GetOrderHistoryInputPort,
    )
    from usecase.port.list_products_port import ListProductsInputPort
    from usecase.port.place_order_port import PlaceOrderInputPort
    from usecase.port.remove_from_cart_port import (
        RemoveFromCartInputPort,
    )
    from usecase.port.view_cart_port import ViewCartInputPort


class OrderController:
    """注文システムのコントローラー.

    Parameters
    ----------
    list_products_input_port : ListProductsInputPort
        商品一覧取得入力ポート。
    add_to_cart_input_port : AddToCartInputPort
        カート追加入力ポート。
    remove_from_cart_input_port : RemoveFromCartInputPort
        カート削除入力ポート。
    view_cart_input_port : ViewCartInputPort
        カート表示入力ポート。
    place_order_input_port : PlaceOrderInputPort
        注文確定入力ポート。
    get_order_history_input_port : GetOrderHistoryInputPort
        注文履歴取得入力ポート。
    """

    def __init__(
        self,
        list_products_input_port: ListProductsInputPort,
        add_to_cart_input_port: AddToCartInputPort,
        remove_from_cart_input_port: RemoveFromCartInputPort,
        view_cart_input_port: ViewCartInputPort,
        place_order_input_port: PlaceOrderInputPort,
        get_order_history_input_port: GetOrderHistoryInputPort,
    ) -> None:
        self.list_products_input_port = list_products_input_port
        self.add_to_cart_input_port = add_to_cart_input_port
        self.remove_from_cart_input_port = remove_from_cart_input_port
        self.view_cart_input_port = view_cart_input_port
        self.place_order_input_port = place_order_input_port
        self.get_order_history_input_port = get_order_history_input_port

    def list_products(self) -> None:
        """商品一覧ユースケースを呼び出す."""
        request = ListProductsRequestDTO()
        self.list_products_input_port.execute(request)

    def add_to_cart(
        self, user_id: str, product_id: str, quantity: int
    ) -> None:
        """カート追加ユースケースを呼び出す.

        Parameters
        ----------
        user_id : str
            ユーザーID。
        product_id : str
            商品ID。
        quantity : int
            数量。
        """
        request = AddToCartRequestDTO(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
        )
        self.add_to_cart_input_port.execute(request)

    def remove_from_cart(self, user_id: str, product_id: str) -> None:
        """カート削除ユースケースを呼び出す.

        Parameters
        ----------
        user_id : str
            ユーザーID。
        product_id : str
            商品ID。
        """
        request = RemoveFromCartRequestDTO(
            user_id=user_id,
            product_id=product_id,
        )
        self.remove_from_cart_input_port.execute(request)

    def view_cart(self, user_id: str) -> None:
        """カート表示ユースケースを呼び出す.

        Parameters
        ----------
        user_id : str
            ユーザーID。
        """
        request = ViewCartRequestDTO(user_id=user_id)
        self.view_cart_input_port.execute(request)

    def place_order(self, user_id: str) -> None:
        """注文確定ユースケースを呼び出す.

        Parameters
        ----------
        user_id : str
            ユーザーID。
        """
        request = PlaceOrderRequestDTO(user_id=user_id)
        self.place_order_input_port.execute(request)

    def get_order_history(self, user_id: str) -> None:
        """注文履歴取得ユースケースを呼び出す.

        Parameters
        ----------
        user_id : str
            ユーザーID。
        """
        request = GetOrderHistoryRequestDTO(user_id=user_id)
        self.get_order_history_input_port.execute(request)
