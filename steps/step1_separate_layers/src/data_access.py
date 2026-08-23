"""Data access layer for Step 1.

インメモリデータへのアクセスを担当するモジュール。
"""

from typing import Any

# ---------------------------------------------------------------------------
# インメモリ「データベース」(グローバル状態)
# ---------------------------------------------------------------------------

products: dict[str, dict[str, Any]] = {
    "P001": {"name": "Tシャツ", "price": 2000, "stock": 10},
    "P002": {"name": "マグカップ", "price": 1500, "stock": 5},
    "P003": {"name": "ステッカー", "price": 500, "stock": 20},
}

carts: dict[str, list[dict[str, Any]]] = {}

orders: dict[str, dict[str, Any]] = {}


def get_all_products() -> dict[str, dict[str, Any]]:
    """
    全ての商品情報を取得する.

    Returns
    -------
    dict[str, dict[str, Any]]
        商品IDをキーとした商品情報の辞書。
    """
    return products


def get_product(product_id: str) -> dict[str, Any] | None:
    """
    指定された商品IDの商品情報を取得する.

    Parameters
    ----------
    product_id : str
        取得したい商品のID。

    Returns
    -------
    dict[str, Any] | None
        商品情報が存在する場合はその辞書、存在しない場合はNone。
    """
    return products.get(product_id)


def update_product_stock(product_id: str, quantity: int) -> None:
    """
    指定された商品IDの在庫数を減算する.

    Parameters
    ----------
    product_id : str
        在庫を減らしたい商品のID。
    quantity : int
        減らす数量。
    """
    if product_id in products:
        products[product_id]["stock"] -= quantity


def get_cart(user_id: str) -> list[dict[str, Any]]:
    """
    指定されたユーザーのカート情報を取得する.

    カートが存在しない場合は空のリストを返す。

    Parameters
    ----------
    user_id : str
        ユーザーID。

    Returns
    -------
    list[dict[str, Any]]
        カート内の商品情報のリスト。
    """
    return carts.get(user_id, [])


def add_to_cart(user_id: str, product_id: str, quantity: int) -> None:
    """
    ユーザーのカートに商品を追加する.

    Parameters
    ----------
    user_id : str
        ユーザーID。
    product_id : str
        追加する商品のID。
    quantity : int
        追加する数量。
    """
    if user_id not in carts:
        carts[user_id] = []

    # 既にカートにある場合は数量を加算
    for item in carts[user_id]:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            return

    carts[user_id].append(
        {
            "product_id": product_id,
            "quantity": quantity,
        }
    )


def remove_from_cart(user_id: str, product_id: str) -> None:
    """
    ユーザーのカートから商品を削除する.

    Parameters
    ----------
    user_id : str
        ユーザーID。
    product_id : str
        削除する商品のID。
    """
    if user_id in carts:
        carts[user_id] = [
            item for item in carts[user_id] if item["product_id"] != product_id
        ]


def clear_cart(user_id: str) -> None:
    """
    ユーザーのカートを空にする.

    Parameters
    ----------
    user_id : str
        ユーザーID。
    """
    carts[user_id] = []


def save_order(order: dict[str, Any]) -> None:
    """
    注文情報を保存する.

    Parameters
    ----------
    order : dict[str, Any]
        保存する注文情報の辞書。
    """
    orders[order["order_id"]] = order


def get_all_orders() -> dict[str, dict[str, Any]]:
    """
    全ての注文情報を取得する.

    Returns
    -------
    dict[str, dict[str, Any]]
        注文IDをキーとした注文情報の辞書。
    """
    return orders
