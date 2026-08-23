"""Step 1: データアクセス層のテスト."""

import data_access


def test_update_product_stock_invalid_product() -> None:
    """存在しない商品の在庫を更新しようとした場合は何もしないこと."""
    # エラーにならないことを確認
    data_access.update_product_stock("INVALID", 1)


def test_remove_from_cart_empty_cart() -> None:
    """カートが存在しないユーザーのカートから削除しようとした場合は何もしないこと."""
    # エラーにならないことを確認
    data_access.remove_from_cart("user2", "P001")
