"""steps/step7_over_engineering のテスト用 conftest."""

import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

# このステップの src/ を Python パスに追加する
sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent / "src"),
)

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

if TYPE_CHECKING:
    from domain.gateway import (
        ICartGateway,
        IOrderGateway,
        IProductGateway,
    )


@pytest.fixture
def product_gateway() -> InMemoryProductGateway:
    """初期商品データを持つ InMemoryProductGateway を提供する."""
    return InMemoryProductGateway()


@pytest.fixture
def cart_gateway() -> InMemoryCartGateway:
    """空の InMemoryCartGateway を提供する."""
    return InMemoryCartGateway()


@pytest.fixture
def order_gateway() -> InMemoryOrderGateway:
    """空の InMemoryOrderGateway を提供する."""
    return InMemoryOrderGateway()


@pytest.fixture
def list_products_presenter() -> ListProductsPresenter:
    """ListProductsPresenter インスタンスを提供する."""
    return ListProductsPresenter()


@pytest.fixture
def add_to_cart_presenter() -> AddToCartPresenter:
    """AddToCartPresenter インスタンスを提供する."""
    return AddToCartPresenter()


@pytest.fixture
def remove_from_cart_presenter() -> RemoveFromCartPresenter:
    """RemoveFromCartPresenter インスタンスを提供する."""
    return RemoveFromCartPresenter()


@pytest.fixture
def view_cart_presenter() -> ViewCartPresenter:
    """ViewCartPresenter インスタンスを提供する."""
    return ViewCartPresenter()


@pytest.fixture
def place_order_presenter() -> PlaceOrderPresenter:
    """PlaceOrderPresenter インスタンスを提供する."""
    return PlaceOrderPresenter()


@pytest.fixture
def get_order_history_presenter() -> GetOrderHistoryPresenter:
    """GetOrderHistoryPresenter インスタンスを提供する."""
    return GetOrderHistoryPresenter()


@pytest.fixture
def list_products_interactor(
    product_gateway: IProductGateway,
    list_products_presenter: ListProductsPresenter,
) -> ListProductsInteractor:
    """ListProductsInteractor インスタンスを提供する."""
    return ListProductsInteractor(
        product_gateway=product_gateway,
        output_port=list_products_presenter,
    )


@pytest.fixture
def add_to_cart_interactor(
    product_gateway: IProductGateway,
    cart_gateway: ICartGateway,
    add_to_cart_presenter: AddToCartPresenter,
) -> AddToCartInteractor:
    """AddToCartInteractor インスタンスを提供する."""
    return AddToCartInteractor(
        product_gateway=product_gateway,
        cart_gateway=cart_gateway,
        output_port=add_to_cart_presenter,
    )


@pytest.fixture
def remove_from_cart_interactor(
    cart_gateway: ICartGateway,
    remove_from_cart_presenter: RemoveFromCartPresenter,
) -> RemoveFromCartInteractor:
    """RemoveFromCartInteractor インスタンスを提供する."""
    return RemoveFromCartInteractor(
        cart_gateway=cart_gateway,
        output_port=remove_from_cart_presenter,
    )


@pytest.fixture
def view_cart_interactor(
    cart_gateway: ICartGateway,
    product_gateway: IProductGateway,
    view_cart_presenter: ViewCartPresenter,
) -> ViewCartInteractor:
    """ViewCartInteractor インスタンスを提供する."""
    return ViewCartInteractor(
        cart_gateway=cart_gateway,
        product_gateway=product_gateway,
        output_port=view_cart_presenter,
    )


@pytest.fixture
def place_order_interactor(
    cart_gateway: ICartGateway,
    product_gateway: IProductGateway,
    order_gateway: IOrderGateway,
    place_order_presenter: PlaceOrderPresenter,
) -> PlaceOrderInteractor:
    """PlaceOrderInteractor インスタンスを提供する."""
    return PlaceOrderInteractor(
        cart_gateway=cart_gateway,
        product_gateway=product_gateway,
        order_gateway=order_gateway,
        output_port=place_order_presenter,
    )


@pytest.fixture
def get_order_history_interactor(
    order_gateway: IOrderGateway,
    get_order_history_presenter: GetOrderHistoryPresenter,
) -> GetOrderHistoryInteractor:
    """GetOrderHistoryInteractor インスタンスを提供する."""
    return GetOrderHistoryInteractor(
        order_gateway=order_gateway,
        output_port=get_order_history_presenter,
    )


@pytest.fixture
def controller(
    list_products_interactor: ListProductsInteractor,
    add_to_cart_interactor: AddToCartInteractor,
    remove_from_cart_interactor: RemoveFromCartInteractor,
    view_cart_interactor: ViewCartInteractor,
    place_order_interactor: PlaceOrderInteractor,
    get_order_history_interactor: GetOrderHistoryInteractor,
) -> OrderController:
    """OrderController インスタンスを提供する."""
    return OrderController(
        list_products_input_port=list_products_interactor,
        add_to_cart_input_port=add_to_cart_interactor,
        remove_from_cart_input_port=remove_from_cart_interactor,
        view_cart_input_port=view_cart_interactor,
        place_order_input_port=place_order_interactor,
        get_order_history_input_port=get_order_history_interactor,
    )


@pytest.fixture
def cli(
    controller: OrderController,
    list_products_presenter: ListProductsPresenter,
    add_to_cart_presenter: AddToCartPresenter,
    remove_from_cart_presenter: RemoveFromCartPresenter,
    view_cart_presenter: ViewCartPresenter,
    place_order_presenter: PlaceOrderPresenter,
    get_order_history_presenter: GetOrderHistoryPresenter,
) -> CLI:
    """CLI インスタンスを提供する."""
    return CLI(
        controller=controller,
        list_products_presenter=list_products_presenter,
        add_to_cart_presenter=add_to_cart_presenter,
        remove_from_cart_presenter=remove_from_cart_presenter,
        view_cart_presenter=view_cart_presenter,
        place_order_presenter=place_order_presenter,
        get_order_history_presenter=get_order_history_presenter,
    )
