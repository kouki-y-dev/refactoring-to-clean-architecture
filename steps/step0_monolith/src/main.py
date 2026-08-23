"""EC order system - Step 0: Monolith.

All features are tightly coupled in a single file.
Business logic, data access, and presentation are not separated.
"""

from datetime import datetime

# ---------------------------------------------------------------------------
# インメモリ「データベース」(グローバル状態)
# ---------------------------------------------------------------------------

products: dict[str, dict] = {
    "P001": {"name": "Tシャツ", "price": 2000, "stock": 10},
    "P002": {"name": "マグカップ", "price": 1500, "stock": 5},
    "P003": {"name": "ステッカー", "price": 500, "stock": 20},
}

carts: dict[str, list[dict]] = {}

orders: dict[str, dict] = {}

TAX_RATE = 0.10

# ---------------------------------------------------------------------------
# 商品一覧
# ---------------------------------------------------------------------------


def list_products() -> None:
    """
    商品一覧を表示する.

    グローバル変数 ``products`` の全商品を stdout に出力する。
    """
    print("=== 商品一覧 ===")
    for product_id, product in products.items():
        print(
            f"  {product_id}: {product['name']}"
            f" - ¥{product['price']}"
            f" (在庫: {product['stock']})"
        )


# ---------------------------------------------------------------------------
# カート操作
# ---------------------------------------------------------------------------


def add_to_cart(
    user_id: str,
    product_id: str,
    quantity: int,
) -> None:
    """
    カートに商品を追加する.

    Parameters
    ----------
    user_id : str
        ユーザー ID。
    product_id : str
        商品 ID。
    quantity : int
        追加する数量。
    """
    if product_id not in products:
        print(f"エラー: 商品 {product_id} が見つかりません")
        return

    if products[product_id]["stock"] < quantity:
        print(
            f"エラー: {products[product_id]['name']} の在庫が不足しています"
            f"(残り {products[product_id]['stock']}個)"
        )
        return

    if user_id not in carts:
        carts[user_id] = []

    # 既にカートにある場合は数量を加算
    for item in carts[user_id]:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            print(
                f"カート更新: {products[product_id]['name']}"
                f" x {item['quantity']}"
            )
            return

    carts[user_id].append(
        {
            "product_id": product_id,
            "quantity": quantity,
        }
    )
    print(f"カート追加: {products[product_id]['name']} x {quantity}")


def remove_from_cart(user_id: str, product_id: str) -> None:
    """
    カートから商品を削除する.

    Parameters
    ----------
    user_id : str
        ユーザー ID。
    product_id : str
        削除する商品 ID。
    """
    if user_id not in carts or not carts[user_id]:
        print("エラー: カートが空です")
        return

    original_len = len(carts[user_id])
    carts[user_id] = [
        item for item in carts[user_id] if item["product_id"] != product_id
    ]

    if len(carts[user_id]) == original_len:
        print(f"エラー: 商品 {product_id} はカートにありません")
        return

    print(f"カートから削除しました: {product_id}")


def view_cart(user_id: str) -> None:
    """
    カートの内容を表示する.

    Parameters
    ----------
    user_id : str
        ユーザー ID。
    """
    if user_id not in carts or not carts[user_id]:
        print("カートは空です")
        return

    print(f"=== {user_id} のカート ===")
    subtotal = 0
    for item in carts[user_id]:
        product = products[item["product_id"]]
        item_total = product["price"] * item["quantity"]
        subtotal += item_total
        print(f"  {product['name']} x {item['quantity']} = ¥{item_total}")

    tax = int(subtotal * TAX_RATE)
    print(f"  小計: ¥{subtotal}")
    print(f"  消費税: ¥{tax}")
    print(f"  合計: ¥{subtotal + tax}")


# ---------------------------------------------------------------------------
# 注文
# ---------------------------------------------------------------------------


def place_order(user_id: str) -> None:
    """
    注文を確定する.

    在庫チェック・合計金額計算・注文作成・在庫減少・カートクリアを行う。

    Parameters
    ----------
    user_id : str
        ユーザー ID。
    """
    if user_id not in carts or not carts[user_id]:
        print("エラー: カートが空です")
        return

    # 在庫チェック
    for item in carts[user_id]:
        product = products[item["product_id"]]
        if product["stock"] < item["quantity"]:
            print(
                f"エラー: {product['name']} の在庫が不足しています"
                f"(残り {product['stock']}個)"
            )
            return

    # 合計金額の計算
    subtotal = 0
    order_items = []
    for item in carts[user_id]:
        product = products[item["product_id"]]
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
    order_id = f"ORD-{len(orders) + 1:04d}"
    orders[order_id] = {
        "order_id": order_id,
        "user_id": user_id,
        "items": order_items,
        "subtotal": subtotal,
        "tax": tax,
        "total": total,
        "created_at": datetime.now(),  # noqa: DTZ005
    }

    # 在庫の減少
    for item in carts[user_id]:
        products[item["product_id"]]["stock"] -= item["quantity"]

    # カートのクリア
    carts[user_id] = []

    print(f"注文が確定しました: {order_id}")
    print(f"合計: ¥{total}(税込)")


# ---------------------------------------------------------------------------
# 注文履歴
# ---------------------------------------------------------------------------


def view_order_history(user_id: str) -> None:
    """
    注文履歴を表示する.

    Parameters
    ----------
    user_id : str
        ユーザー ID。
    """
    user_orders = {
        oid: order
        for oid, order in orders.items()
        if order["user_id"] == user_id
    }

    if not user_orders:
        print("注文履歴はありません")
        return

    print(f"=== {user_id} の注文履歴 ===")
    for order_id, order in user_orders.items():
        print(f"  {order_id} ({order['created_at']}) - ¥{order['total']}")
        for item in order["items"]:
            print(
                f"    {item['name']}"
                f" x {item['quantity']}"
                f" = ¥{item['subtotal']}"
            )


# ---------------------------------------------------------------------------
# CLI メニュー
# ---------------------------------------------------------------------------


def main() -> None:
    """
    簡易 CLI メニュー.

    対話型ループで商品一覧・カート操作・注文・履歴参照を行う。
    """
    user_id = "user1"

    while True:
        print("\n--- EC サイト注文システム ---")
        print("1. 商品一覧")
        print("2. カートに追加")
        print("3. カートから削除")
        print("4. カート表示")
        print("5. 注文確定")
        print("6. 注文履歴")
        print("0. 終了")

        choice = input("選択してください: ").strip()

        if choice == "1":
            list_products()
        elif choice == "2":
            product_id = input("商品ID: ").strip()
            quantity = int(input("数量: ").strip())
            add_to_cart(user_id, product_id, quantity)
        elif choice == "3":
            product_id = input("商品ID: ").strip()
            remove_from_cart(user_id, product_id)
        elif choice == "4":
            view_cart(user_id)
        elif choice == "5":
            place_order(user_id)
        elif choice == "6":
            view_order_history(user_id)
        elif choice == "0":
            print("終了します")
            break
        else:
            print("無効な選択です")


if __name__ == "__main__":
    main()
