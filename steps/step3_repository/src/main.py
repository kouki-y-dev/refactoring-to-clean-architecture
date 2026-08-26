"""Step 3 エントリーポイント.

リポジトリ、サービス、CLI のインスタンス化と
依存性の注入 (Composition Root) を行い、
アプリケーションを起動します。
"""

from cli import CLI
from repository.cart_repository import CartRepository
from repository.order_repository import OrderRepository
from repository.product_repository import ProductRepository
from service import ShopService


def main() -> None:
    """アプリケーションのエントリーポイント."""
    product_repo = ProductRepository()
    cart_repo = CartRepository()
    order_repo = OrderRepository()

    service = ShopService(
        product_repo=product_repo,
        cart_repo=cart_repo,
        order_repo=order_repo,
    )

    cli = CLI(service=service)
    cli.main_menu()


if __name__ == "__main__":
    main()
