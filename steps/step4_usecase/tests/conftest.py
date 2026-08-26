"""steps/step4_usecase のテスト用 conftest."""

import sys
from pathlib import Path

import pytest

# このステップの src/ を Python パスに追加する
sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent / "src"),
)

from cli import CLI
from repository.cart_repository import CartRepository
from repository.order_repository import OrderRepository
from repository.product_repository import ProductRepository
from usecase.add_to_cart import AddToCartUseCase
from usecase.get_order_history import GetOrderHistoryUseCase
from usecase.list_products import ListProductsUseCase
from usecase.place_order import PlaceOrderUseCase
from usecase.remove_from_cart import RemoveFromCartUseCase
from usecase.view_cart import ViewCartUseCase


@pytest.fixture
def product_repo() -> ProductRepository:
    """初期商品データを持つ ProductRepository を提供する."""
    return ProductRepository()


@pytest.fixture
def cart_repo() -> CartRepository:
    """空の CartRepository を提供する."""
    return CartRepository()


@pytest.fixture
def order_repo() -> OrderRepository:
    """空の OrderRepository を提供する."""
    return OrderRepository()


@pytest.fixture
def list_products_usecase(
    product_repo: ProductRepository,
) -> ListProductsUseCase:
    """ListProductsUseCase インスタンスを提供する."""
    return ListProductsUseCase(product_repo=product_repo)


@pytest.fixture
def add_to_cart_usecase(
    product_repo: ProductRepository, cart_repo: CartRepository
) -> AddToCartUseCase:
    """AddToCartUseCase インスタンスを提供する."""
    return AddToCartUseCase(product_repo=product_repo, cart_repo=cart_repo)


@pytest.fixture
def remove_from_cart_usecase(
    cart_repo: CartRepository,
) -> RemoveFromCartUseCase:
    """RemoveFromCartUseCase インスタンスを提供する."""
    return RemoveFromCartUseCase(cart_repo=cart_repo)


@pytest.fixture
def view_cart_usecase(
    cart_repo: CartRepository, product_repo: ProductRepository
) -> ViewCartUseCase:
    """ViewCartUseCase インスタンスを提供する."""
    return ViewCartUseCase(cart_repo=cart_repo, product_repo=product_repo)


@pytest.fixture
def place_order_usecase(
    cart_repo: CartRepository,
    product_repo: ProductRepository,
    order_repo: OrderRepository,
) -> PlaceOrderUseCase:
    """PlaceOrderUseCase インスタンスを提供する."""
    return PlaceOrderUseCase(
        cart_repo=cart_repo,
        product_repo=product_repo,
        order_repo=order_repo,
    )


@pytest.fixture
def get_order_history_usecase(
    order_repo: OrderRepository,
) -> GetOrderHistoryUseCase:
    """GetOrderHistoryUseCase インスタンスを提供する."""
    return GetOrderHistoryUseCase(order_repo=order_repo)


@pytest.fixture
def cli(
    list_products_usecase: ListProductsUseCase,
    add_to_cart_usecase: AddToCartUseCase,
    remove_from_cart_usecase: RemoveFromCartUseCase,
    view_cart_usecase: ViewCartUseCase,
    place_order_usecase: PlaceOrderUseCase,
    get_order_history_usecase: GetOrderHistoryUseCase,
) -> CLI:
    """ユースケース群を注入した CLI インスタンスを提供する."""
    return CLI(
        list_products_usecase=list_products_usecase,
        add_to_cart_usecase=add_to_cart_usecase,
        remove_from_cart_usecase=remove_from_cart_usecase,
        view_cart_usecase=view_cart_usecase,
        place_order_usecase=place_order_usecase,
        get_order_history_usecase=get_order_history_usecase,
    )
