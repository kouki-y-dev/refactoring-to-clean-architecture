"""steps/step6_clean_architecture のテスト用 conftest."""

import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

# このステップの src/ を Python パスに追加する
sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent / "src"),
)

from infrastructure.repository.cart_repository import (
    InMemoryCartRepository,
)
from infrastructure.repository.order_repository import (
    InMemoryOrderRepository,
)
from infrastructure.repository.product_repository import (
    InMemoryProductRepository,
)
from presentation.cli import CLI
from usecase.add_to_cart import AddToCartUseCase
from usecase.get_order_history import GetOrderHistoryUseCase
from usecase.list_products import ListProductsUseCase
from usecase.place_order import PlaceOrderUseCase
from usecase.remove_from_cart import RemoveFromCartUseCase
from usecase.view_cart import ViewCartUseCase

if TYPE_CHECKING:
    from domain.repository import (
        ICartRepository,
        IOrderRepository,
        IProductRepository,
    )


@pytest.fixture
def product_repo() -> InMemoryProductRepository:
    """初期商品データを持つ InMemoryProductRepository を提供する."""
    return InMemoryProductRepository()


@pytest.fixture
def cart_repo() -> InMemoryCartRepository:
    """空の InMemoryCartRepository を提供する."""
    return InMemoryCartRepository()


@pytest.fixture
def order_repo() -> InMemoryOrderRepository:
    """空の InMemoryOrderRepository を提供する."""
    return InMemoryOrderRepository()


@pytest.fixture
def list_products_usecase(
    product_repo: IProductRepository,
) -> ListProductsUseCase:
    """ListProductsUseCase インスタンスを提供する."""
    return ListProductsUseCase(product_repo=product_repo)


@pytest.fixture
def add_to_cart_usecase(
    product_repo: IProductRepository, cart_repo: ICartRepository
) -> AddToCartUseCase:
    """AddToCartUseCase インスタンスを提供する."""
    return AddToCartUseCase(product_repo=product_repo, cart_repo=cart_repo)


@pytest.fixture
def remove_from_cart_usecase(
    cart_repo: ICartRepository,
) -> RemoveFromCartUseCase:
    """RemoveFromCartUseCase インスタンスを提供する."""
    return RemoveFromCartUseCase(cart_repo=cart_repo)


@pytest.fixture
def view_cart_usecase(
    cart_repo: ICartRepository, product_repo: IProductRepository
) -> ViewCartUseCase:
    """ViewCartUseCase インスタンスを提供する."""
    return ViewCartUseCase(cart_repo=cart_repo, product_repo=product_repo)


@pytest.fixture
def place_order_usecase(
    cart_repo: ICartRepository,
    product_repo: IProductRepository,
    order_repo: IOrderRepository,
) -> PlaceOrderUseCase:
    """PlaceOrderUseCase インスタンスを提供する."""
    return PlaceOrderUseCase(
        cart_repo=cart_repo,
        product_repo=product_repo,
        order_repo=order_repo,
    )


@pytest.fixture
def get_order_history_usecase(
    order_repo: IOrderRepository,
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
