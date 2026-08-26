"""steps/step3_repository のテスト用 conftest."""

import sys
from pathlib import Path

import pytest

# このステップの src/ を Python パスに追加する
sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent / "src"),
)

from repository.cart_repository import CartRepository
from repository.order_repository import OrderRepository
from repository.product_repository import ProductRepository
from service import ShopService


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
def shop_service(
    product_repo: ProductRepository,
    cart_repo: CartRepository,
    order_repo: OrderRepository,
) -> ShopService:
    """初期状態の各リポジトリを注入した ShopService を提供する."""
    return ShopService(
        product_repo=product_repo,
        cart_repo=cart_repo,
        order_repo=order_repo,
    )
