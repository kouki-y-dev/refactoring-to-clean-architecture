"""steps/step1_separate_layers のテスト用 conftest."""

import sys
from pathlib import Path

import pytest

# このステップの src/ を Python パスに追加する
sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent / "src"),
)


@pytest.fixture(autouse=True)
def _reset_global_state() -> None:
    """グローバル状態を初期値にリセットする."""
    import data_access

    data_access.products.clear()
    data_access.products.update(
        {
            "P001": {
                "name": "Tシャツ",
                "price": 2000,
                "stock": 10,
            },
            "P002": {
                "name": "マグカップ",
                "price": 1500,
                "stock": 5,
            },
            "P003": {
                "name": "ステッカー",
                "price": 500,
                "stock": 20,
            },
        }
    )
    data_access.carts.clear()
    data_access.orders.clear()
