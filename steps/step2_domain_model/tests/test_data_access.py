"""Step 2: データアクセス層のテスト."""

import data_access


def test_update_product_stock_invalid_product() -> None:
    """存在しない商品の在庫を更新しようとした場合は何もしないこと."""
    # エラーにならないことを確認
    data_access.update_product_stock("INVALID", 1)


def test_remove_from_cart_nonexistent_item() -> None:
    """カート内に存在しない商品を削除しようとした場合 ValueError になること."""
    import pytest

    # まずカートにアイテムを追加してカートを作成
    data_access.add_to_cart("user1", "P001", 1)
    with pytest.raises(ValueError, match="カートにありません"):
        data_access.remove_from_cart("user1", "P999")
