"""プレゼンテーション層の CLI (View) モジュール.

クリーンアーキテクチャの Interface Adapters / UI レイヤーを担当します。
ユーザー入力を受け取り、コントローラー (Controller) を呼び出し、
各ユースケースのプレゼンター (Presenter) が生成した View Model を
画面に出力します。
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from presentation.controller.order_controller import OrderController
    from presentation.presenter.add_to_cart_presenter import (
        AddToCartPresenter,
    )
    from presentation.presenter.get_order_history_presenter import (
        GetOrderHistoryPresenter,
    )
    from presentation.presenter.list_products_presenter import (
        ListProductsPresenter,
    )
    from presentation.presenter.place_order_presenter import (
        PlaceOrderPresenter,
    )
    from presentation.presenter.remove_from_cart_presenter import (
        RemoveFromCartPresenter,
    )
    from presentation.presenter.view_cart_presenter import (
        ViewCartPresenter,
    )


class CLI:
    """EC サイトのコマンドラインインターフェース (View).

    Parameters
    ----------
    controller : OrderController
        注文システムコントローラー。
    list_products_presenter : ListProductsPresenter
        商品一覧プレゼンター。
    add_to_cart_presenter : AddToCartPresenter
        カート追加プレゼンター。
    remove_from_cart_presenter : RemoveFromCartPresenter
        カート削除プレゼンター。
    view_cart_presenter : ViewCartPresenter
        カート表示プレゼンター。
    place_order_presenter : PlaceOrderPresenter
        注文確定プレゼンター。
    get_order_history_presenter : GetOrderHistoryPresenter
        注文履歴プレゼンター。
    user_id : str, optional
        操作対象のデフォルトユーザーID。デフォルトは 'user1'。
    """

    def __init__(
        self,
        controller: OrderController,
        list_products_presenter: ListProductsPresenter,
        add_to_cart_presenter: AddToCartPresenter,
        remove_from_cart_presenter: RemoveFromCartPresenter,
        view_cart_presenter: ViewCartPresenter,
        place_order_presenter: PlaceOrderPresenter,
        get_order_history_presenter: GetOrderHistoryPresenter,
        user_id: str = "user1",
    ) -> None:
        self.controller = controller
        self.list_products_presenter = list_products_presenter
        self.add_to_cart_presenter = add_to_cart_presenter
        self.remove_from_cart_presenter = remove_from_cart_presenter
        self.view_cart_presenter = view_cart_presenter
        self.place_order_presenter = place_order_presenter
        self.get_order_history_presenter = get_order_history_presenter
        self.user_id = user_id

    def list_products(self) -> None:
        """商品一覧を表示する."""
        self.controller.list_products()
        vm = self.list_products_presenter.view_model
        if not vm.is_success:
            print(vm.error_message)
            return

        print("=== 商品一覧 ===")
        for p in vm.products:
            print(
                f"  {p.product_id}: {p.name} - {p.price_display} "
                f"(在庫: {p.stock_display})"
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
            追加数量。
        """
        self.controller.add_to_cart(user_id, product_id, quantity)
        vm = self.add_to_cart_presenter.view_model
        if vm.is_success:
            print(vm.message)
        else:
            print(vm.error_message)

    def remove_from_cart(self, user_id: str, product_id: str) -> None:
        """カートから商品を削除する.

        Parameters
        ----------
        user_id : str
            ユーザーID。
        product_id : str
            商品ID。
        """
        self.controller.remove_from_cart(user_id, product_id)
        vm = self.remove_from_cart_presenter.view_model
        if vm.is_success:
            print(vm.message)
        else:
            print(vm.error_message)

    def view_cart(self, user_id: str) -> None:
        """カートの内容を表示する.

        Parameters
        ----------
        user_id : str
            ユーザーID。
        """
        self.controller.view_cart(user_id)
        vm = self.view_cart_presenter.view_model
        if not vm.is_success:
            print(vm.error_message)
            return

        if vm.is_empty:
            print("カートは空です")
            return

        print(f"=== {user_id} のカート ===")
        for item in vm.items:
            print(
                f"  {item.name} x {item.quantity_display} = "
                f"{item.total_display}"
            )

        print(f"  小計: {vm.subtotal_display}")
        print(f"  消費税: {vm.tax_display}")
        print(f"  合計: {vm.total_display}")

    def place_order(self, user_id: str) -> None:
        """注文を確定する.

        Parameters
        ----------
        user_id : str
            ユーザーID。
        """
        self.controller.place_order(user_id)
        vm = self.place_order_presenter.view_model
        if vm.is_success:
            print(f"注文が確定しました: {vm.order_id}")
            print(f"合計: {vm.total_display}(税込)")
        else:
            print(vm.error_message)

    def view_order_history(self, user_id: str) -> None:
        """注文履歴を表示する.

        Parameters
        ----------
        user_id : str
            ユーザーID。
        """
        self.controller.get_order_history(user_id)
        vm = self.get_order_history_presenter.view_model
        if not vm.is_success:
            print(vm.error_message)
            return

        if not vm.orders:
            print("注文履歴はありません")
            return

        print(f"=== {user_id} の注文履歴 ===")
        for order in vm.orders:
            print(
                f"  {order.order_id} ({order.created_at_display}) - "
                f"{order.total_display}"
            )
            for item in order.items:
                print(
                    f"    {item.name} x {item.quantity} = "
                    f"{item.subtotal_display}"
                )

    def main_menu(self) -> None:
        """簡易 CLI メニュー."""
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
