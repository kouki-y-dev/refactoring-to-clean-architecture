"""Presentation layer tests for Step 7."""

from datetime import datetime
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

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
from usecase.port.add_to_cart_port import AddToCartResponseDTO
from usecase.port.get_order_history_port import (
    GetOrderHistoryResponseDTO,
    OrderHistoryItemDTO,
)
from usecase.port.list_products_port import (
    ListProductsResponseDTO,
    ProductItemDTO,
)
from usecase.port.place_order_port import (
    OrderItemDTO,
    PlaceOrderResponseDTO,
)
from usecase.port.remove_from_cart_port import RemoveFromCartResponseDTO
from usecase.port.view_cart_port import (
    CartDetailItemDTO,
    ViewCartResponseDTO,
)

if TYPE_CHECKING:
    import pytest
    from presentation.cli.cli import CLI


class TestPresenters:
    """Presenter 各クラスの単体テスト."""

    def test_list_products_presenter_success(self) -> None:
        presenter = ListProductsPresenter()
        response = ListProductsResponseDTO(
            products=[
                ProductItemDTO(
                    product_id="P001", name="Tシャツ", price=2000, stock=10
                )
            ]
        )
        presenter.present_success(response)
        assert presenter.view_model.is_success is True
        assert len(presenter.view_model.products) == 1
        assert presenter.view_model.products[0].price_display == "¥2000"

    def test_list_products_presenter_error(self) -> None:
        presenter = ListProductsPresenter()
        presenter.present_error("商品取得エラー")
        assert presenter.view_model.is_success is False
        assert presenter.view_model.error_message == "商品取得エラー"

    def test_add_to_cart_presenter(self) -> None:
        presenter = AddToCartPresenter()
        presenter.present_success(
            AddToCartResponseDTO(
                product_id="P001",
                product_name="Tシャツ",
                price=2000,
                quantity=1,
                stock=10,
            )
        )
        assert presenter.view_model.is_success is True
        assert "Tシャツ" in presenter.view_model.message

        presenter.present_error("在庫不足")
        assert presenter.view_model.is_success is False
        assert presenter.view_model.error_message == "在庫不足"

    def test_remove_from_cart_presenter(self) -> None:
        presenter = RemoveFromCartPresenter()
        presenter.present_success(RemoveFromCartResponseDTO(product_id="P001"))
        assert presenter.view_model.is_success is True
        assert "P001" in presenter.view_model.message

        presenter.present_error("商品なし")
        assert presenter.view_model.is_success is False
        assert presenter.view_model.error_message == "商品なし"

    def test_view_cart_presenter(self) -> None:
        presenter = ViewCartPresenter()
        presenter.present_success(
            ViewCartResponseDTO(
                is_empty=False,
                user_id="user1",
                items=[
                    CartDetailItemDTO(
                        product_id="P001",
                        name="Tシャツ",
                        price=2000,
                        quantity=2,
                        item_total=4000,
                    )
                ],
                subtotal=4000,
                tax=400,
                total=4400,
            )
        )
        assert presenter.view_model.is_empty is False
        assert presenter.view_model.total_display == "¥4400"

        presenter.present_error("カートエラー")
        assert presenter.view_model.is_success is False

    def test_place_order_presenter(self) -> None:
        presenter = PlaceOrderPresenter()
        now = datetime(2026, 1, 1, tzinfo=ZoneInfo("Asia/Tokyo"))
        presenter.present_success(
            PlaceOrderResponseDTO(
                order_id="ord_001",
                user_id="user1",
                items=[
                    OrderItemDTO(
                        product_id="P001",
                        name="Tシャツ",
                        price=2000,
                        quantity=1,
                        subtotal=2000,
                    )
                ],
                subtotal=2000,
                tax=200,
                total=2200,
                created_at=now,
            )
        )
        assert presenter.view_model.is_success is True
        assert presenter.view_model.order_id == "ord_001"
        assert presenter.view_model.total_display == "¥2200"

        presenter.present_error("注文失敗")
        assert presenter.view_model.is_success is False

    def test_get_order_history_presenter(self) -> None:
        presenter = GetOrderHistoryPresenter()
        now = datetime(2026, 1, 1, tzinfo=ZoneInfo("Asia/Tokyo"))
        presenter.present_success(
            GetOrderHistoryResponseDTO(
                orders=[
                    OrderHistoryItemDTO(
                        order_id="ord_001",
                        user_id="user1",
                        items=[
                            OrderItemDTO(
                                product_id="P001",
                                name="Tシャツ",
                                price=2000,
                                quantity=1,
                                subtotal=2000,
                            )
                        ],
                        subtotal=2000,
                        tax=200,
                        total=2200,
                        created_at=now,
                    )
                ]
            )
        )
        assert presenter.view_model.is_success is True
        assert len(presenter.view_model.orders) == 1

        presenter.present_error("履歴取得失敗")
        assert presenter.view_model.is_success is False


class TestCLI:
    """CLI クラスのテスト."""

    def test_list_products_output(
        self, cli: CLI, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """商品一覧が正しく表示される."""
        cli.list_products()
        captured = capsys.readouterr()
        assert "=== 商品一覧 ===" in captured.out
        assert "P001: Tシャツ - ¥2000 (在庫: 10)" in captured.out

    def test_list_products_error_output(
        self,
        cli: CLI,
        list_products_presenter: ListProductsPresenter,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """商品一覧エラー時の表示."""
        list_products_presenter.present_error("商品取得エラー発生")
        monkeypatch.setattr(cli.controller, "list_products", lambda: None)
        cli.list_products()
        captured = capsys.readouterr()
        assert "商品取得エラー発生" in captured.out

    def test_add_to_cart_success_output(
        self, cli: CLI, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """カート追加成功メッセージが表示される."""
        cli.add_to_cart("user1", "P001", 2)
        captured = capsys.readouterr()
        assert "カートに追加/更新しました: Tシャツ" in captured.out

    def test_add_to_cart_error_output(
        self, cli: CLI, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """カート追加失敗エラーが表示される."""
        cli.add_to_cart("user1", "P999", 1)
        captured = capsys.readouterr()
        assert "エラー: 商品 P999 が見つかりません" in captured.out

    def test_remove_from_cart_output(
        self, cli: CLI, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """カート削除メッセージが表示される."""
        cli.add_to_cart("user1", "P001", 1)
        capsys.readouterr()

        cli.remove_from_cart("user1", "P001")
        captured = capsys.readouterr()
        assert "カートから削除しました: P001" in captured.out

    def test_remove_from_cart_error_output(
        self, cli: CLI, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """カート削除エラーメッセージが表示される."""
        cli.remove_from_cart("user1", "P001")
        captured = capsys.readouterr()
        assert "エラー: 商品 P001 はカートにありません" in captured.out

    def test_view_cart_empty_output(
        self, cli: CLI, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """空カートの表示."""
        cli.view_cart("user1")
        captured = capsys.readouterr()
        assert "カートは空です" in captured.out

    def test_view_cart_error_output(
        self,
        cli: CLI,
        view_cart_presenter: ViewCartPresenter,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """カート表示エラー時の出力."""
        view_cart_presenter.present_error("カート表示エラー")
        monkeypatch.setattr(cli.controller, "view_cart", lambda _: None)
        cli.view_cart("user1")
        captured = capsys.readouterr()
        assert "カート表示エラー" in captured.out

    def test_view_cart_with_items_output(
        self, cli: CLI, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """アイテム入りカートの表示."""
        cli.add_to_cart("user1", "P001", 2)
        capsys.readouterr()

        cli.view_cart("user1")
        captured = capsys.readouterr()
        assert "=== user1 のカート ===" in captured.out
        assert "Tシャツ x 2 = ¥4000" in captured.out
        assert "小計: ¥4000" in captured.out
        assert "消費税: ¥400" in captured.out
        assert "合計: ¥4400" in captured.out

    def test_place_order_success_output(
        self, cli: CLI, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """注文確定成功メッセージが表示される."""
        cli.add_to_cart("user1", "P001", 1)
        capsys.readouterr()

        cli.place_order("user1")
        captured = capsys.readouterr()
        assert "注文が確定しました: ord_001" in captured.out
        assert "合計: ¥2200(税込)" in captured.out

    def test_place_order_error_output(
        self, cli: CLI, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """注文確定失敗エラーが表示される."""
        cli.place_order("user1")
        captured = capsys.readouterr()
        assert "エラー: カートが空です" in captured.out

    def test_view_order_history_empty_output(
        self, cli: CLI, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """注文履歴なしの表示."""
        cli.view_order_history("user1")
        captured = capsys.readouterr()
        assert "注文履歴はありません" in captured.out

    def test_view_order_history_error_output(
        self,
        cli: CLI,
        get_order_history_presenter: GetOrderHistoryPresenter,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """注文履歴取得エラー時の表示."""
        get_order_history_presenter.present_error("履歴取得エラー")
        monkeypatch.setattr(
            cli.controller, "get_order_history", lambda _: None
        )
        cli.view_order_history("user1")
        captured = capsys.readouterr()
        assert "履歴取得エラー" in captured.out

    def test_view_order_history_with_orders_output(
        self, cli: CLI, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """注文履歴ありの表示."""
        cli.add_to_cart("user1", "P001", 1)
        cli.place_order("user1")
        capsys.readouterr()

        cli.view_order_history("user1")
        captured = capsys.readouterr()
        assert "=== user1 の注文履歴 ===" in captured.out
        assert "ord_001" in captured.out
        assert "Tシャツ x 1 = ¥2000" in captured.out


class TestCLIMenu:
    """CLI 対話型メニューのテスト."""

    def test_main_menu_flow(
        self,
        cli: CLI,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """メインメニューで各操作を選択して終了する一連のフローをテスト."""
        inputs = iter(
            [
                "1",  # 商品一覧
                "2",  # カート追加
                "P001",  # 商品ID
                "2",  # 数量
                "4",  # カート表示
                "3",  # カート削除
                "P001",  # 商品ID
                "2",  # カート追加
                "P002",  # 商品ID
                "1",  # 数量
                "5",  # 注文確定
                "6",  # 注文履歴
                "99",  # 無効な選択
                "0",  # 終了
            ]
        )
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        cli.main_menu()
        captured = capsys.readouterr()

        assert "--- EC サイト注文システム ---" in captured.out
        assert "=== 商品一覧 ===" in captured.out
        assert "カートに追加/更新しました: Tシャツ" in captured.out
        assert "カートから削除しました: P001" in captured.out
        assert "注文が確定しました: ord_001" in captured.out
        assert "=== user1 の注文履歴 ===" in captured.out
        assert "無効な選択です" in captured.out
        assert "終了します" in captured.out
