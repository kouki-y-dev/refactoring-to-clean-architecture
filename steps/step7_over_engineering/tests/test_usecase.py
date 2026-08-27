"""UseCase layer tests for Step 7."""

from typing import TYPE_CHECKING

from domain.entity import Product
from usecase.interactor.add_to_cart_interactor import AddToCartInteractor
from usecase.port.add_to_cart_port import (
    AddToCartOutputPort,
    AddToCartRequestDTO,
    AddToCartResponseDTO,
)
from usecase.port.get_order_history_port import (
    GetOrderHistoryRequestDTO,
)
from usecase.port.list_products_port import (
    ListProductsRequestDTO,
)
from usecase.port.place_order_port import (
    PlaceOrderRequestDTO,
)
from usecase.port.remove_from_cart_port import (
    RemoveFromCartRequestDTO,
)
from usecase.port.view_cart_port import (
    ViewCartRequestDTO,
)

if TYPE_CHECKING:
    from infrastructure.gateway.cart_gateway import InMemoryCartGateway
    from infrastructure.gateway.product_gateway import InMemoryProductGateway
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
    from usecase.interactor.get_order_history_interactor import (
        GetOrderHistoryInteractor,
    )
    from usecase.interactor.list_products_interactor import (
        ListProductsInteractor,
    )
    from usecase.interactor.place_order_interactor import (
        PlaceOrderInteractor,
    )
    from usecase.interactor.remove_from_cart_interactor import (
        RemoveFromCartInteractor,
    )
    from usecase.interactor.view_cart_interactor import (
        ViewCartInteractor,
    )


class TestListProductsInteractor:
    """ListProductsInteractor のテスト."""

    def test_list_products_success(
        self,
        list_products_interactor: ListProductsInteractor,
        list_products_presenter: ListProductsPresenter,
    ) -> None:
        """商品一覧取得が成功し Presenter に通知される."""
        request = ListProductsRequestDTO()
        list_products_interactor.execute(request)

        vm = list_products_presenter.view_model
        assert vm.is_success is True
        assert len(vm.products) == 3
        assert vm.products[0].name == "Tシャツ"
        assert vm.products[0].price_display == "¥2000"


class TestAddToCartInteractor:
    """AddToCartInteractor のテスト."""

    def test_add_to_cart_success(
        self,
        add_to_cart_interactor: AddToCartInteractor,
        add_to_cart_presenter: AddToCartPresenter,
    ) -> None:
        """商品をカートに追加できる."""
        request = AddToCartRequestDTO(
            user_id="user1", product_id="P001", quantity=2
        )
        add_to_cart_interactor.execute(request)

        vm = add_to_cart_presenter.view_model
        assert vm.is_success is True
        assert "Tシャツ" in vm.message

    def test_add_to_cart_product_not_found(
        self,
        add_to_cart_interactor: AddToCartInteractor,
        add_to_cart_presenter: AddToCartPresenter,
    ) -> None:
        """存在しない商品の場合はエラーが通知される."""
        request = AddToCartRequestDTO(
            user_id="user1", product_id="P999", quantity=1
        )
        add_to_cart_interactor.execute(request)

        vm = add_to_cart_presenter.view_model
        assert vm.is_success is False
        assert "商品 P999 が見つかりません" in vm.error_message

    def test_add_to_cart_insufficient_stock(
        self,
        add_to_cart_interactor: AddToCartInteractor,
        add_to_cart_presenter: AddToCartPresenter,
    ) -> None:
        """在庫不足の場合はエラーが通知される."""
        request = AddToCartRequestDTO(
            user_id="user1", product_id="P001", quantity=20
        )
        add_to_cart_interactor.execute(request)

        vm = add_to_cart_presenter.view_model
        assert vm.is_success is False
        assert "在庫が不足しています" in vm.error_message

    def test_add_to_cart_custom_fake_output_port(
        self,
        product_gateway: InMemoryProductGateway,
        cart_gateway: InMemoryCartGateway,
    ) -> None:
        """独自の Fake Output Port を使った独立テスト."""

        class FakeAddToCartOutputPort(AddToCartOutputPort):
            def __init__(self) -> None:
                self.received_response: AddToCartResponseDTO | None = None
                self.received_error: str | None = None

            def present_success(self, response: AddToCartResponseDTO) -> None:
                self.received_response = response

            def present_error(self, error_message: str) -> None:
                self.received_error = error_message

        fake_port = FakeAddToCartOutputPort()
        interactor = AddToCartInteractor(
            product_gateway=product_gateway,
            cart_gateway=cart_gateway,
            output_port=fake_port,
        )

        request = AddToCartRequestDTO(
            user_id="user1", product_id="P001", quantity=1
        )
        interactor.execute(request)

        assert fake_port.received_response is not None
        assert fake_port.received_response.product_name == "Tシャツ"
        assert fake_port.received_error is None


class TestRemoveFromCartInteractor:
    """RemoveFromCartInteractor のテスト."""

    def test_remove_from_cart_success(
        self,
        add_to_cart_interactor: AddToCartInteractor,
        remove_from_cart_interactor: RemoveFromCartInteractor,
        remove_from_cart_presenter: RemoveFromCartPresenter,
    ) -> None:
        """カートから商品を削除できる."""
        add_to_cart_interactor.execute(
            AddToCartRequestDTO(user_id="user1", product_id="P001", quantity=1)
        )

        remove_from_cart_interactor.execute(
            RemoveFromCartRequestDTO(user_id="user1", product_id="P001")
        )

        vm = remove_from_cart_presenter.view_model
        assert vm.is_success is True
        assert "カートから削除しました: P001" in vm.message

    def test_remove_from_cart_user_cart_not_found(
        self,
        remove_from_cart_interactor: RemoveFromCartInteractor,
        remove_from_cart_presenter: RemoveFromCartPresenter,
    ) -> None:
        """カート自体が存在しないユーザーが削除しようとするとエラーが通知される."""
        remove_from_cart_interactor.execute(
            RemoveFromCartRequestDTO(
                user_id="nonexistent_user", product_id="P001"
            )
        )

        vm = remove_from_cart_presenter.view_model
        assert vm.is_success is False
        assert "カートにありません" in vm.error_message

    def test_remove_from_cart_item_not_found_in_existing_cart(
        self,
        add_to_cart_interactor: AddToCartInteractor,
        remove_from_cart_interactor: RemoveFromCartInteractor,
        remove_from_cart_presenter: RemoveFromCartPresenter,
    ) -> None:
        """カートはあるが該当商品が入っていない場合.

        ValueError がキャッチされエラー通知される。
        """
        add_to_cart_interactor.execute(
            AddToCartRequestDTO(user_id="user1", product_id="P001", quantity=1)
        )

        remove_from_cart_interactor.execute(
            RemoveFromCartRequestDTO(user_id="user1", product_id="P002")
        )

        vm = remove_from_cart_presenter.view_model
        assert vm.is_success is False
        assert "カートにありません" in vm.error_message


class TestViewCartInteractor:
    """ViewCartInteractor のテスト."""

    def test_view_cart_empty(
        self,
        view_cart_interactor: ViewCartInteractor,
        view_cart_presenter: ViewCartPresenter,
    ) -> None:
        """空のカートを表示できる."""
        view_cart_interactor.execute(ViewCartRequestDTO(user_id="user1"))

        vm = view_cart_presenter.view_model
        assert vm.is_success is True
        assert vm.is_empty is True

    def test_view_cart_with_items(
        self,
        add_to_cart_interactor: AddToCartInteractor,
        view_cart_interactor: ViewCartInteractor,
        view_cart_presenter: ViewCartPresenter,
    ) -> None:
        """アイテムが入ったカートを表示できる."""
        add_to_cart_interactor.execute(
            AddToCartRequestDTO(user_id="user1", product_id="P001", quantity=1)
        )
        add_to_cart_interactor.execute(
            AddToCartRequestDTO(user_id="user1", product_id="P002", quantity=2)
        )

        view_cart_interactor.execute(ViewCartRequestDTO(user_id="user1"))

        vm = view_cart_presenter.view_model
        assert vm.is_success is True
        assert vm.is_empty is False
        assert len(vm.items) == 2
        assert vm.subtotal_display == "¥4400"
        assert vm.tax_display == "¥440"
        assert vm.total_display == "¥4840"

    def test_view_cart_with_deleted_product(
        self,
        cart_gateway: InMemoryCartGateway,
        view_cart_interactor: ViewCartInteractor,
        view_cart_presenter: ViewCartPresenter,
    ) -> None:
        """カート内に存在しない商品IDが入っている場合スキップされる."""
        cart = cart_gateway.get_or_create("user1")
        cart.add_item("P999", 1)
        cart_gateway.save(cart)

        view_cart_interactor.execute(ViewCartRequestDTO(user_id="user1"))

        vm = view_cart_presenter.view_model
        assert vm.is_success is True
        assert len(vm.items) == 0


class TestPlaceOrderInteractor:
    """PlaceOrderInteractor のテスト."""

    def test_place_order_success(
        self,
        add_to_cart_interactor: AddToCartInteractor,
        place_order_interactor: PlaceOrderInteractor,
        place_order_presenter: PlaceOrderPresenter,
        product_gateway: InMemoryProductGateway,
        cart_gateway: InMemoryCartGateway,
    ) -> None:
        """注文が確定し、在庫が減少しカートがクリアされる."""
        add_to_cart_interactor.execute(
            AddToCartRequestDTO(user_id="user1", product_id="P001", quantity=2)
        )

        place_order_interactor.execute(PlaceOrderRequestDTO(user_id="user1"))

        vm = place_order_presenter.view_model
        assert vm.is_success is True
        assert vm.order_id == "ord_001"
        assert vm.total_display == "¥4400"

        # 在庫減少の確認
        product = product_gateway.find_by_id("P001")
        assert product is not None
        assert product.stock == 8

        # カートクリアの確認
        cart = cart_gateway.find_by_user_id("user1")
        assert cart is not None
        assert cart.is_empty is True

    def test_place_order_empty_cart(
        self,
        place_order_interactor: PlaceOrderInteractor,
        place_order_presenter: PlaceOrderPresenter,
    ) -> None:
        """空のカートで注文するとエラーが通知される."""
        place_order_interactor.execute(PlaceOrderRequestDTO(user_id="user1"))

        vm = place_order_presenter.view_model
        assert vm.is_success is False
        assert "カートが空です" in vm.error_message

    def test_place_order_product_not_found(
        self,
        cart_gateway: InMemoryCartGateway,
        place_order_interactor: PlaceOrderInteractor,
        place_order_presenter: PlaceOrderPresenter,
    ) -> None:
        """存在しない商品のカートアイテムで注文するとエラーが通知される."""
        cart = cart_gateway.get_or_create("user1")
        cart.add_item("P999", 1)
        cart_gateway.save(cart)

        place_order_interactor.execute(PlaceOrderRequestDTO(user_id="user1"))

        vm = place_order_presenter.view_model
        assert vm.is_success is False
        assert "商品 P999 が見つかりません" in vm.error_message

    def test_place_order_stock_insufficient(
        self,
        product_gateway: InMemoryProductGateway,
        cart_gateway: InMemoryCartGateway,
        place_order_interactor: PlaceOrderInteractor,
        place_order_presenter: PlaceOrderPresenter,
    ) -> None:
        """カート追加後に在庫が減少し不足した場合、エラーが通知される."""
        cart = cart_gateway.get_or_create("user1")
        cart.add_item("P001", 5)
        cart_gateway.save(cart)

        # 在庫を強制的に減らす
        product_gateway.save(
            Product(id="P001", name="Tシャツ", price=2000, stock=2)
        )

        place_order_interactor.execute(PlaceOrderRequestDTO(user_id="user1"))

        vm = place_order_presenter.view_model
        assert vm.is_success is False
        assert "在庫が不足しています" in vm.error_message


class TestGetOrderHistoryInteractor:
    """GetOrderHistoryInteractor のテスト."""

    def test_get_order_history_empty(
        self,
        get_order_history_interactor: GetOrderHistoryInteractor,
        get_order_history_presenter: GetOrderHistoryPresenter,
    ) -> None:
        """注文履歴がない場合、空リストが通知される."""
        get_order_history_interactor.execute(
            GetOrderHistoryRequestDTO(user_id="user1")
        )

        vm = get_order_history_presenter.view_model
        assert vm.is_success is True
        assert len(vm.orders) == 0

    def test_get_order_history_with_orders(
        self,
        add_to_cart_interactor: AddToCartInteractor,
        place_order_interactor: PlaceOrderInteractor,
        get_order_history_interactor: GetOrderHistoryInteractor,
        get_order_history_presenter: GetOrderHistoryPresenter,
    ) -> None:
        """注文確定後に注文履歴が取得できる."""
        add_to_cart_interactor.execute(
            AddToCartRequestDTO(user_id="user1", product_id="P001", quantity=1)
        )
        place_order_interactor.execute(PlaceOrderRequestDTO(user_id="user1"))

        get_order_history_interactor.execute(
            GetOrderHistoryRequestDTO(user_id="user1")
        )

        vm = get_order_history_presenter.view_model
        assert vm.is_success is True
        assert len(vm.orders) == 1
        assert vm.orders[0].order_id == "ord_001"
        assert vm.orders[0].total_display == "¥2200"
