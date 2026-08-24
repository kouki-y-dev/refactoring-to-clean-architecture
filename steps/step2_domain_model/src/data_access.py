"""Data access layer for Step 2.

インメモリデータへのアクセスを担当するモジュール。
Step 1 との主な違いは、辞書ではなく Pydantic ドメインモデルの
インスタンスを保持・返却する点です。
"""

from domain.entity import Cart, Order, Product

# ---------------------------------------------------------------------------
# インメモリ「データベース」(グローバル状態)
# ---------------------------------------------------------------------------

products: dict[str, Product] = {
    "P001": Product(id="P001", name="Tシャツ", price=2000, stock=10),
    "P002": Product(id="P002", name="マグカップ", price=1500, stock=5),
    "P003": Product(id="P003", name="ステッカー", price=500, stock=20),
}

carts: dict[str, Cart] = {}

orders: dict[str, Order] = {}


def get_all_products() -> dict[str, Product]:
    """
    全ての商品情報を取得する.

    Returns
    -------
    dict[str, Product]
        商品IDをキーとした商品情報の辞書。
    """
    return products


def get_product(product_id: str) -> Product | None:
    """
    指定された商品IDの商品情報を取得する.

    Parameters
    ----------
    product_id : str
        取得したい商品のID。

    Returns
    -------
    Product | None
        商品情報が存在する場合はその Product、存在しない場合は None。
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
    product = products.get(product_id)
    if product is not None:
        product.decrease_stock(quantity)


def get_cart(user_id: str) -> Cart:
    """
    指定されたユーザーのカート情報を取得する.

    カートが存在しない場合は空のカートを返す。

    Parameters
    ----------
    user_id : str
        ユーザーID。

    Returns
    -------
    Cart
        ユーザーのカート。
    """
    if user_id not in carts:
        carts[user_id] = Cart(user_id=user_id)
    return carts[user_id]


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
    cart = get_cart(user_id)
    cart.add_item(product_id, quantity)


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
    cart = get_cart(user_id)
    cart.remove_item(product_id)


def clear_cart(user_id: str) -> None:
    """
    ユーザーのカートを空にする.

    Parameters
    ----------
    user_id : str
        ユーザーID。
    """
    cart = get_cart(user_id)
    cart.clear()


def save_order(order: Order) -> None:
    """
    注文情報を保存する.

    Parameters
    ----------
    order : Order
        保存する注文エンティティ。
    """
    orders[order.order_id] = order


def get_all_orders() -> dict[str, Order]:
    """
    全ての注文情報を取得する.

    Returns
    -------
    dict[str, Order]
        注文IDをキーとした注文情報の辞書。
    """
    return orders
