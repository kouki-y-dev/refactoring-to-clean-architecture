"""Step 4 エントリーポイント.

リポジトリ、各ユースケース、CLI のインスタンス化と
依存性の注入 (Composition Root) を行い、
アプリケーションを起動します。
"""

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


def main() -> None:
    """アプリケーションのエントリーポイント."""
    # 1. リポジトリの初期化
    product_repo = ProductRepository()
    cart_repo = CartRepository()
    order_repo = OrderRepository()

    # 2. 各ユースケースの初期化 (必要なリポジトリを注入)
    list_products_usecase = ListProductsUseCase(product_repo=product_repo)
    add_to_cart_usecase = AddToCartUseCase(
        product_repo=product_repo, cart_repo=cart_repo
    )
    remove_from_cart_usecase = RemoveFromCartUseCase(cart_repo=cart_repo)
    view_cart_usecase = ViewCartUseCase(
        cart_repo=cart_repo, product_repo=product_repo
    )
    place_order_usecase = PlaceOrderUseCase(
        cart_repo=cart_repo,
        product_repo=product_repo,
        order_repo=order_repo,
    )
    get_order_history_usecase = GetOrderHistoryUseCase(order_repo=order_repo)

    # 3. CLI の初期化 (ユースケース群を注入)
    cli = CLI(
        list_products_usecase=list_products_usecase,
        add_to_cart_usecase=add_to_cart_usecase,
        remove_from_cart_usecase=remove_from_cart_usecase,
        view_cart_usecase=view_cart_usecase,
        place_order_usecase=place_order_usecase,
        get_order_history_usecase=get_order_history_usecase,
    )

    # 4. メインメニューの起動
    cli.main_menu()


if __name__ == "__main__":
    main()
