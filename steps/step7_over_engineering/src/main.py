"""Step 7 エントリーポイント (Composition Root).

過剰な抽象化 (Over-Engineering) を施したクリーンアーキテクチャの全レイヤー
(Gateway, Presenter, Interactor, Controller, CLI) の
インスタンス化と依存性の注入を行い、アプリケーションを起動します。
"""

from infrastructure.gateway.cart_gateway import InMemoryCartGateway
from infrastructure.gateway.order_gateway import InMemoryOrderGateway
from infrastructure.gateway.product_gateway import (
    InMemoryProductGateway,
)
from presentation.cli.cli import CLI
from presentation.controller.order_controller import OrderController
from presentation.presenter.add_to_cart_presenter import AddToCartPresenter
from presentation.presenter.get_order_history_presenter import (
    GetOrderHistoryPresenter,
)
from presentation.presenter.list_products_presenter import (
    ListProductsPresenter,
)
from presentation.presenter.place_order_presenter import PlaceOrderPresenter
from presentation.presenter.remove_from_cart_presenter import (
    RemoveFromCartPresenter,
)
from presentation.presenter.view_cart_presenter import ViewCartPresenter
from usecase.interactor.add_to_cart_interactor import AddToCartInteractor
from usecase.interactor.get_order_history_interactor import (
    GetOrderHistoryInteractor,
)
from usecase.interactor.list_products_interactor import (
    ListProductsInteractor,
)
from usecase.interactor.place_order_interactor import PlaceOrderInteractor
from usecase.interactor.remove_from_cart_interactor import (
    RemoveFromCartInteractor,
)
from usecase.interactor.view_cart_interactor import ViewCartInteractor


def main() -> None:
    """アプリケーションのエントリーポイント (Composition Root)."""
    # 1. インフラ層: 具象ゲートウェイの初期化
    product_gateway = InMemoryProductGateway()
    cart_gateway = InMemoryCartGateway()
    order_gateway = InMemoryOrderGateway()

    # 2. プレゼンテーション層: 各ユースケース用プレゼンターの初期化
    list_products_presenter = ListProductsPresenter()
    add_to_cart_presenter = AddToCartPresenter()
    remove_from_cart_presenter = RemoveFromCartPresenter()
    view_cart_presenter = ViewCartPresenter()
    place_order_presenter = PlaceOrderPresenter()
    get_order_history_presenter = GetOrderHistoryPresenter()

    # 3. ユースケース層: インターラクターの初期化
    list_products_interactor = ListProductsInteractor(
        product_gateway=product_gateway,
        output_port=list_products_presenter,
    )
    add_to_cart_interactor = AddToCartInteractor(
        product_gateway=product_gateway,
        cart_gateway=cart_gateway,
        output_port=add_to_cart_presenter,
    )
    remove_from_cart_interactor = RemoveFromCartInteractor(
        cart_gateway=cart_gateway,
        output_port=remove_from_cart_presenter,
    )
    view_cart_interactor = ViewCartInteractor(
        cart_gateway=cart_gateway,
        product_gateway=product_gateway,
        output_port=view_cart_presenter,
    )
    place_order_interactor = PlaceOrderInteractor(
        cart_gateway=cart_gateway,
        product_gateway=product_gateway,
        order_gateway=order_gateway,
        output_port=place_order_presenter,
    )
    get_order_history_interactor = GetOrderHistoryInteractor(
        order_gateway=order_gateway,
        output_port=get_order_history_presenter,
    )

    # 4. プレゼンテーション層: コントローラーの初期化
    controller = OrderController(
        list_products_input_port=list_products_interactor,
        add_to_cart_input_port=add_to_cart_interactor,
        remove_from_cart_input_port=remove_from_cart_interactor,
        view_cart_input_port=view_cart_interactor,
        place_order_input_port=place_order_interactor,
        get_order_history_input_port=get_order_history_interactor,
    )

    # 5. プレゼンテーション層: CLI (View) の初期化
    cli = CLI(
        controller=controller,
        list_products_presenter=list_products_presenter,
        add_to_cart_presenter=add_to_cart_presenter,
        remove_from_cart_presenter=remove_from_cart_presenter,
        view_cart_presenter=view_cart_presenter,
        place_order_presenter=place_order_presenter,
        get_order_history_presenter=get_order_history_presenter,
    )

    # 6. アプリケーション起動
    cli.main_menu()


if __name__ == "__main__":
    main()
