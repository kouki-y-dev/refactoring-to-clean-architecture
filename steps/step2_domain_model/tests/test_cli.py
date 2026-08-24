"""Step 2: CLI 層 (Presentation Layer) のテスト.

プレゼンテーション層 (cli.py) をテストします。
UI に特化したテストのため、主に標準出力の内容を検証します。
"""

from typing import TYPE_CHECKING

import cli
import service

if TYPE_CHECKING:
    import pytest
    from pytest_mock import MockerFixture


class TestListProducts:
    """商品一覧表示のテスト."""

    def test_displays_all_products(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """全商品が正しくフォーマットされて表示されること."""
        cli.list_products()
        captured = capsys.readouterr()

        assert "=== 商品一覧 ===" in captured.out
        assert "Tシャツ" in captured.out
        assert "マグカップ" in captured.out
        assert "ステッカー" in captured.out
        assert "¥2000" in captured.out


class TestAddToCart:
    """カート追加表示のテスト."""

    def test_adds_item_and_prints_success(
        self,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """カート追加成功時の出力が正しいこと."""
        mocker.patch("builtins.input", side_effect=["P001", "2"])
        cli.add_to_cart("user1", "P001", 2)
        captured = capsys.readouterr()

        assert "カートに追加/更新しました" in captured.out
        assert "Tシャツ" in captured.out

    def test_prints_error_for_invalid_product(
        self,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """存在しない商品の場合にエラーメッセージが出力されること."""
        mocker.patch("builtins.input", side_effect=["P999", "1"])
        cli.add_to_cart("user1", "P999", 1)
        captured = capsys.readouterr()

        assert "エラー: 商品 P999 が見つかりません" in captured.out


class TestRemoveFromCart:
    """カート削除表示のテスト."""

    def test_removes_item_and_prints_success(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """カート削除成功時の出力が正しいこと."""
        service.add_item_to_cart("user1", "P001", 1)

        capsys.readouterr()  # 追加時の出力をクリア
        cli.remove_from_cart("user1", "P001")
        captured = capsys.readouterr()

        assert "カートから削除しました: P001" in captured.out

    def test_prints_error_for_empty_cart(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """空カートから削除した場合のエラー出力が正しいこと."""
        cli.remove_from_cart("user1", "P001")
        captured = capsys.readouterr()

        assert "エラー: カートが空です" in captured.out


class TestViewCart:
    """カート表示のテスト."""

    def test_displays_cart_with_totals(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """カート内容と金額が正しく表示されること."""
        service.add_item_to_cart("user1", "P001", 2)
        service.add_item_to_cart("user1", "P003", 3)

        capsys.readouterr()
        cli.view_cart("user1")
        captured = capsys.readouterr()

        assert "=== user1 のカート ===" in captured.out
        assert "Tシャツ x 2 = ¥4000" in captured.out
        assert "ステッカー x 3 = ¥1500" in captured.out
        assert "小計: ¥5500" in captured.out
        assert "消費税: ¥550" in captured.out
        assert "合計: ¥6050" in captured.out

    def test_displays_empty_cart_message(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """空カートの場合のメッセージが表示されること."""
        cli.view_cart("user1")
        captured = capsys.readouterr()

        assert "カートは空です" in captured.out


class TestPlaceOrder:
    """注文確定表示のテスト."""

    def test_creates_order_and_prints_success(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """注文確定成功時の出力が正しいこと."""
        service.add_item_to_cart("user1", "P001", 1)

        capsys.readouterr()
        cli.place_order("user1")
        captured = capsys.readouterr()

        assert "注文が確定しました: ORD-" in captured.out
        assert "合計: ¥2200(税込)" in captured.out

    def test_prints_error_when_cart_empty(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """カートが空の場合のエラー出力が正しいこと."""
        cli.place_order("user1")
        captured = capsys.readouterr()

        assert "エラー: カートが空です" in captured.out


class TestViewOrderHistory:
    """注文履歴表示のテスト."""

    def test_displays_order_history(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """注文履歴が正しく表示されること."""
        service.add_item_to_cart("user1", "P001", 1)
        service.place_order("user1")

        capsys.readouterr()
        cli.view_order_history("user1")
        captured = capsys.readouterr()

        assert "=== user1 の注文履歴 ===" in captured.out
        assert "ORD-" in captured.out
        assert "Tシャツ x 1 = ¥2000" in captured.out

    def test_displays_empty_history_message(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """注文履歴がない場合のメッセージが表示されること."""
        cli.view_order_history("user1")
        captured = capsys.readouterr()

        assert "注文履歴はありません" in captured.out


class TestMainMenu:
    """メインメニュー表示と操作のテスト."""

    def test_main_menu_interactions(
        self, mocker: MockerFixture, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """メニューからの各種操作が正しく呼び出されること."""
        # 操作のシナリオ:
        # 1. 商品一覧 (1)
        # 2. カートに追加 (2 -> P001 -> 1)
        # 3. カートから削除 (3 -> P001)
        # 4. カート表示 (4)
        # 5. 無効な選択 (99)
        # 6. 注文確定 (5) -> カート空で失敗
        # 7. 注文履歴 (6)
        # 8. 終了 (0)
        mocker.patch(
            "builtins.input",
            side_effect=[
                "1",
                "2",
                "P001",
                "1",
                "3",
                "P001",
                "4",
                "99",
                "5",
                "6",
                "0",
            ],
        )

        cli.main_menu()
        captured = capsys.readouterr()

        assert "=== 商品一覧 ===" in captured.out
        assert "カートに追加/更新しました" in captured.out
        assert "カートから削除しました" in captured.out
        assert "カートは空です" in captured.out
        assert "無効な選択です" in captured.out
        assert "エラー: カートが空です" in captured.out
        assert "注文履歴はありません" in captured.out
        assert "終了します" in captured.out
