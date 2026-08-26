"""Presentation layer (CLI) for Step 4.

ユーザーインターフェースを担当するモジュール。
ユーザー入力を受け取り、各ユースケース (UseCase) を呼び出し、
結果を画面 (stdout) に出力します。
リポジトリなどの低層モジュールには直接依存せず、ユースケース層のみに依存します。
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from usecase.add_to_cart import AddToCartUseCase
    from usecase.get_order_history import GetOrderHistoryUseCase
    from usecase.list_products import ListProductsUseCase
    from usecase.place_order import PlaceOrderUseCase
    from usecase.remove_from_cart import RemoveFromCartUseCase
    from usecase.view_cart import ViewCartUseCase


class CLI:
    """EC サイトのコマンドラインインターフェース.

    Parameters
    ----------
    list_products_usecase : ListProductsUseCase
        商品一覧取得ユースケース。
    add_to_cart_usecase : AddToCartUseCase
        カート追加ユースケース。
    remove_from_cart_usecase : RemoveFromCartUseCase
        カート削除ユースケース。
    view_cart_usecase : ViewCartUseCase
        カート表示・詳細取得ユースケース。
    place_order_usecase : PlaceOrderUseCase
        注文確定ユースケース。
    get_order_history_usecase : GetOrderHistoryUseCase
        注文履歴取得ユースケース。
    user_id : str, optional
        操作対象のデフォルトユーザーID。デフォルトは 'user1'。
    """

    def __init__(
        self,
        list_products_usecase: ListProductsUseCase,
        add_to_cart_usecase: AddToCartUseCase,
        remove_from_cart_usecase: RemoveFromCartUseCase,
        view_cart_usecase: ViewCartUseCase,
        place_order_usecase: PlaceOrderUseCase,
        get_order_history_usecase: GetOrderHistoryUseCase,
        user_id: str = "user1",
    ) -> None:
        self.list_products_usecase = list_products_usecase
        self.add_to_cart_usecase = add_to_cart_usecase
        self.remove_from_cart_usecase = remove_from_cart_usecase
        self.view_cart_usecase = view_cart_usecase
        self.place_order_usecase = place_order_usecase
        self.get_order_history_usecase = get_order_history_usecase
        self.user_id = user_id

    def list_products(self) -> None:
        """商品一覧を表示する."""
        products = self.list_products_usecase.execute()
        print("=== 商品一覧 ===")
        for product in products:
            print(
                f"  {product.id}: {product.name}"
                f" - ¥{product.price}"
                f" (在庫: {product.stock})"
            )

    def add_to_cart(
        self, user_id: str, product_id: str, quantity: int
    ) -> None:
        """カートに商品を追加する.

        Parameters
        ----------
        user_id : str
            ユーザーID。
        product_id : str
            商品ID。
        quantity : int
            追加する数量。
        """
        try:
            product = self.add_to_cart_usecase.execute(
                user_id, product_id, quantity
            )
            print(f"カートに追加/更新しました: {product.name}")
        except ValueError as e:
            print(e)

    def remove_from_cart(self, user_id: str, product_id: str) -> None:
        """カートから商品を削除する.

        Parameters
        ----------
        user_id : str
            ユーザーID。
        product_id : str
            削除する商品ID。
        """
        try:
            self.remove_from_cart_usecase.execute(user_id, product_id)
            print(f"カートから削除しました: {product_id}")
        except ValueError as e:
            print(e)

    def view_cart(self, user_id: str) -> None:
        """カートの内容を表示する.

        Parameters
        ----------
        user_id : str
            ユーザーID。
        """
        cart_details = self.view_cart_usecase.execute(user_id)
        if cart_details is None:
            print("カートは空です")
            return

        print(f"=== {user_id} のカート ===")
        for item in cart_details.items:
            print(f"  {item.name} x {item.quantity} = ¥{item.item_total}")

        print(f"  小計: ¥{cart_details.subtotal}")
        print(f"  消費税: ¥{cart_details.tax}")
        print(f"  合計: ¥{cart_details.total}")

    def place_order(self, user_id: str) -> None:
        """注文を確定する.

        Parameters
        ----------
        user_id : str
            ユーザーID。
        """
        try:
            order = self.place_order_usecase.execute(user_id)
            print(f"注文が確定しました: {order.order_id}")
            print(f"合計: ¥{order.total}(税込)")
        except ValueError as e:
            print(e)

    def view_order_history(self, user_id: str) -> None:
        """注文履歴を表示する.

        Parameters
        ----------
        user_id : str
            ユーザーID。
        """
        orders = self.get_order_history_usecase.execute(user_id)
        if not orders:
            print("注文履歴はありません")
            return

        print(f"=== {user_id} の注文履歴 ===")
        for order in orders:
            print(f"  {order.order_id} ({order.created_at}) - ¥{order.total}")
            for item in order.items:
                print(f"    {item.name} x {item.quantity} = ¥{item.subtotal}")

    def main_menu(self) -> None:
        """簡易 CLI メニュー.

        対話型ループで各種操作を行います。
        """
        while True:
            print("\n--- EC サイト注文システム ---")
            print("1. 商品一覧")
            print("2. カートに追加")
            print("3. カートから削除")
            print("4. カート表示")
            print("5. 注文確定")
            print("6. 注文履歴")
            print("0. 終了")

            choice = input("選択してください: ").strip()

            if choice == "1":
                self.list_products()
            elif choice == "2":
                product_id = input("商品ID: ").strip()
                quantity = int(input("数量: ").strip())
                self.add_to_cart(self.user_id, product_id, quantity)
            elif choice == "3":
                product_id = input("商品ID: ").strip()
                self.remove_from_cart(self.user_id, product_id)
            elif choice == "4":
                self.view_cart(self.user_id)
            elif choice == "5":
                self.place_order(self.user_id)
            elif choice == "6":
                self.view_order_history(self.user_id)
            elif choice == "0":
                print("終了します")
                break
            else:
                print("無効な選択です")
