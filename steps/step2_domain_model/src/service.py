"""Service layer for Step 2.

ビジネスロジックを担当するモジュール。
Step 1 との主な違いは、辞書操作の代わりにドメインモデルの
メソッドやファクトリを活用している点です。
"""

import data_access
from domain.entity import (
    TAX_RATE,
    CartDetailItem,
    CartDetails,
    Order,
    OrderItem,
    Product,
)


def get_products_list() -> dict[str, Product]:
    """
    全ての商品情報を取得する.

    Returns
    -------
    dict[str, Product]
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

    if not product.has_enough_stock(quantity):
        msg = (
            f"エラー: {product.name} の在庫が不足しています"
            f"(残り {product.stock}個)"
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
    if cart.is_empty:
        msg = "エラー: カートが空です"
        raise ValueError(msg)

    # remove_item 内で存在チェックと ValueError を raise する
    cart.remove_item(product_id)


def get_cart_details(user_id: str) -> CartDetails | None:
    """
    カートの詳細情報と計算結果(小計、消費税、合計)を取得する.

    Parameters
    ----------
    user_id : str
        ユーザーID。

    Returns
    -------
    CartDetails | None
        カート内の商品詳細と合計金額。カートが空の場合は None。
    """
    cart = data_access.get_cart(user_id)
    if cart.is_empty:
        return None

    subtotal = 0
    items: list[CartDetailItem] = []
    for cart_item in cart.items:
        product = data_access.get_product(cart_item.product_id)
        # 商品が存在することは保証されている前提
        if product is None:
            continue

        item_total = product.price * cart_item.quantity
        subtotal += item_total
        items.append(
            CartDetailItem(
                product_id=cart_item.product_id,
                name=product.name,
                price=product.price,
                quantity=cart_item.quantity,
                item_total=item_total,
            )
        )

    tax = int(subtotal * TAX_RATE)
    return CartDetails(
        items=items,
        subtotal=subtotal,
        tax=tax,
        total=subtotal + tax,
    )


def place_order(user_id: str) -> Order:
    """
    注文を確定するビジネスロジック.

    在庫チェック・合計金額計算・注文作成・在庫減少・カートクリアを行います。

    Parameters
    ----------
    user_id : str
        ユーザーID。

    Returns
    -------
    Order
        作成された注文エンティティ。

    Raises
    ------
    ValueError
        カートが空の場合、または在庫が不足している場合。
    """
    cart = data_access.get_cart(user_id)
    if cart.is_empty:
        msg = "エラー: カートが空です"
        raise ValueError(msg)

    # 在庫チェック
    for cart_item in cart.items:
        product = data_access.get_product(cart_item.product_id)
        if product is None:
            msg = f"エラー: 商品 {cart_item.product_id} が見つかりません"
            raise ValueError(msg)

        if not product.has_enough_stock(cart_item.quantity):
            msg = (
                f"エラー: {product.name} の在庫が不足しています"
                f"(残り {product.stock}個)"
            )
            raise ValueError(msg)

    # 注文アイテムの作成
    order_items: list[OrderItem] = []
    for cart_item in cart.items:
        product = data_access.get_product(cart_item.product_id)
        if product is None:
            continue

        item_total = product.price * cart_item.quantity
        order_items.append(
            OrderItem(
                product_id=cart_item.product_id,
                name=product.name,
                price=product.price,
                quantity=cart_item.quantity,
                subtotal=item_total,
            )
        )

    # 注文の作成 -- 金額計算はドメインファクトリに委譲
    all_orders = data_access.get_all_orders()
    order_id = f"ORD-{len(all_orders) + 1:04d}"
    order = Order.create(
        order_id=order_id,
        user_id=user_id,
        items=order_items,
    )

    data_access.save_order(order)

    # 在庫の減少
    for cart_item in cart.items:
        data_access.update_product_stock(
            cart_item.product_id, cart_item.quantity
        )

    # カートのクリア
    data_access.clear_cart(user_id)

    return order


def get_order_history(user_id: str) -> list[Order]:
    """
    指定されたユーザーの注文履歴を取得する.

    Parameters
    ----------
    user_id : str
        ユーザーID。

    Returns
    -------
    list[Order]
        ユーザーの注文エンティティのリスト。
    """
    all_orders = data_access.get_all_orders()
    return [order for order in all_orders.values() if order.user_id == user_id]
