"""Presentation layer (CLI) for Step 1.

ユーザーインターフェースを担当するモジュール。
ユーザー入力を受け取り、ビジネスロジック (service.py) を呼び出し、
結果を画面 (stdout) に出力します。
"""

import service


def list_products() -> None:
    """商品一覧を表示する."""
    products = service.get_products_list()
    print("=== 商品一覧 ===")
    for product_id, product in products.items():
        print(
            f"  {product_id}: {product['name']}"
            f" - ¥{product['price']}"
            f" (在庫: {product['stock']})"
        )


def add_to_cart(user_id: str, product_id: str, quantity: int) -> None:
    """
    カートに商品を追加する.

    Parameters
    ----------
    user_id : str
        ユーザーID。
    product_id : str
        商品ID。
    quantity : int
        追加する数量。
    """
    try:
        service.add_item_to_cart(user_id, product_id, quantity)
        products = service.get_products_list()
        print(f"カートに追加/更新しました: {products[product_id]['name']}")
    except ValueError as e:
        print(e)


def remove_from_cart(user_id: str, product_id: str) -> None:
    """
    カートから商品を削除する.

    Parameters
    ----------
    user_id : str
        ユーザーID。
    product_id : str
        削除する商品ID。
    """
    try:
        service.remove_item_from_cart(user_id, product_id)
        print(f"カートから削除しました: {product_id}")
    except ValueError as e:
        print(e)


def view_cart(user_id: str) -> None:
    """
    カートの内容を表示する.

    Parameters
    ----------
    user_id : str
        ユーザーID。
    """
    cart_details = service.get_cart_details(user_id)
    if not cart_details:
        print("カートは空です")
        return

    print(f"=== {user_id} のカート ===")
    for item in cart_details["items"]:
        print(f"  {item['name']} x {item['quantity']} = ¥{item['item_total']}")

    print(f"  小計: ¥{cart_details['subtotal']}")
    print(f"  消費税: ¥{cart_details['tax']}")
    print(f"  合計: ¥{cart_details['total']}")


def place_order(user_id: str) -> None:
    """
    注文を確定する.

    Parameters
    ----------
    user_id : str
        ユーザーID。
    """
    try:
        order = service.place_order(user_id)
        print(f"注文が確定しました: {order['order_id']}")
        print(f"合計: ¥{order['total']}(税込)")
    except ValueError as e:
        print(e)


def view_order_history(user_id: str) -> None:
    """
    注文履歴を表示する.

    Parameters
    ----------
    user_id : str
        ユーザーID。
    """
    orders = service.get_order_history(user_id)
    if not orders:
        print("注文履歴はありません")
        return

    print(f"=== {user_id} の注文履歴 ===")
    for order in orders:
        print(
            f"  {order['order_id']} ({order['created_at']}) - "
            f"¥{order['total']}"
        )
        for item in order["items"]:
            print(
                f"    {item['name']}"
                f" x {item['quantity']}"
                f" = ¥{item['subtotal']}"
            )


def main_menu() -> None:
    """
    簡易 CLI メニュー.

    対話型ループで各種操作を行います。
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
