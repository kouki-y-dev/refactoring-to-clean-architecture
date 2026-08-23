"""Service layer for Step 1.

ビジネスロジックを担当するモジュール。
プレゼンテーション層 (CLI) やデータアクセス層の実装には依存せず、
ドメインのルールや計算を実行します。
"""

from datetime import datetime
from typing import Any

import data_access

TAX_RATE = 0.10


def get_products_list() -> dict[str, dict[str, Any]]:
    """
    全ての商品情報を取得する.

    Returns
    -------
    dict[str, dict[str, Any]]
        商品IDをキーとした商品情報の辞書。
    """
    return data_access.get_all_products()


def add_item_to_cart(user_id: str, product_id: str, quantity: int) -> None:
    """
    カートに商品を追加するビジネスロジック.

    商品の存在チェックと在庫チェックを行います。

    Parameters
    ----------
    user_id : str
        ユーザーID。
    product_id : str
        商品ID。
    quantity : int
        追加する数量。

    Raises
    ------
    ValueError
        商品が存在しない場合、または在庫が不足している場合。
    """
    product = data_access.get_product(product_id)
    if product is None:
        msg = f"エラー: 商品 {product_id} が見つかりません"
        raise ValueError(msg)

    if product["stock"] < quantity:
        msg = (
            f"エラー: {product['name']} の在庫が不足しています"
            f"(残り {product['stock']}個)"
        )
        raise ValueError(msg)

    data_access.add_to_cart(user_id, product_id, quantity)


def remove_item_from_cart(user_id: str, product_id: str) -> None:
    """
    カートから商品を削除するビジネスロジック.

    カートが空でないこと、および商品がカート内に存在することを確認します。

    Parameters
    ----------
    user_id : str
        ユーザーID。
    product_id : str
        削除する商品ID。

    Raises
    ------
    ValueError
        カートが空の場合、または商品がカートに存在しない場合。
    """
    cart = data_access.get_cart(user_id)
    if not cart:
        msg = "エラー: カートが空です"
        raise ValueError(msg)

    # カート内に商品が存在するかチェック
    if not any(item["product_id"] == product_id for item in cart):
        msg = f"エラー: 商品 {product_id} はカートにありません"
        raise ValueError(msg)

    data_access.remove_from_cart(user_id, product_id)


def get_cart_details(user_id: str) -> dict[str, Any]:
    """
    カートの詳細情報と計算結果(小計、消費税、合計)を取得する.

    Parameters
    ----------
    user_id : str
        ユーザーID。

    Returns
    -------
    dict[str, Any]
        カート内の商品詳細と合計金額を含む辞書。カートが空の場合は空の辞書を返す。
    """
    cart = data_access.get_cart(user_id)
    if not cart:
        return {}

    subtotal = 0
    items = []
    for item in cart:
        product = data_access.get_product(item["product_id"])
        # 商品が存在することは保証されている前提
        if product is None:
            continue

        item_total = product["price"] * item["quantity"]
        subtotal += item_total
        items.append(
            {
                "product_id": item["product_id"],
                "name": product["name"],
                "price": product["price"],
                "quantity": item["quantity"],
                "item_total": item_total,
            }
        )

    tax = int(subtotal * TAX_RATE)
    return {
        "items": items,
        "subtotal": subtotal,
        "tax": tax,
        "total": subtotal + tax,
    }


def place_order(user_id: str) -> dict[str, Any]:
    """
    注文を確定するビジネスロジック.

    在庫チェック・合計金額計算・注文作成・在庫減少・カートクリアを行います。

    Parameters
    ----------
    user_id : str
        ユーザーID。

    Returns
    -------
    dict[str, Any]
        作成された注文情報の辞書。

    Raises
    ------
    ValueError
        カートが空の場合、または在庫が不足している場合。
    """
    cart = data_access.get_cart(user_id)
    if not cart:
        msg = "エラー: カートが空です"
        raise ValueError(msg)

    # 在庫チェック
    for item in cart:
        product = data_access.get_product(item["product_id"])
        if product is None:
            msg = f"エラー: 商品 {item['product_id']} が見つかりません"
            raise ValueError(msg)

        if product["stock"] < item["quantity"]:
            msg = (
                f"エラー: {product['name']} の在庫が不足しています"
                f"(残り {product['stock']}個)"
            )
            raise ValueError(msg)

    # 合計金額の計算と注文アイテムの作成
    subtotal = 0
    order_items = []
    for item in cart:
        product = data_access.get_product(item["product_id"])
        if product is None:
            continue

        item_total = product["price"] * item["quantity"]
        subtotal += item_total
        order_items.append(
            {
                "product_id": item["product_id"],
                "name": product["name"],
                "price": product["price"],
                "quantity": item["quantity"],
                "subtotal": item_total,
            }
        )

    tax = int(subtotal * TAX_RATE)
    total = subtotal + tax

    # 注文の作成
    orders = data_access.get_all_orders()
    order_id = f"ORD-{len(orders) + 1:04d}"
    order = {
        "order_id": order_id,
        "user_id": user_id,
        "items": order_items,
        "subtotal": subtotal,
        "tax": tax,
        "total": total,
        "created_at": datetime.now(),  # noqa: DTZ005
    }

    data_access.save_order(order)

    # 在庫の減少
    for item in cart:
        data_access.update_product_stock(item["product_id"], item["quantity"])

    # カートのクリア
    data_access.clear_cart(user_id)

    return order


def get_order_history(user_id: str) -> list[dict[str, Any]]:
    """
    指定されたユーザーの注文履歴を取得する.

    Parameters
    ----------
    user_id : str
        ユーザーID。

    Returns
    -------
    list[dict[str, Any]]
        ユーザーの注文情報のリスト。
    """
    orders = data_access.get_all_orders()
    return [order for order in orders.values() if order["user_id"] == user_id]
