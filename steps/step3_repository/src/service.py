"""Service layer for Step 3.

ビジネスロジックを担当するモジュール。
Step 2 との主な違いは、グローバル関数群 (data_access.py) への直接依存を排除し、
リポジトリインスタンス (Repository パターン) を介してデータアクセスと
ドメインモデルの永続化を行う点です。
"""

from typing import TYPE_CHECKING

from domain.entity import (
    TAX_RATE,
    CartDetailItem,
    CartDetails,
    Order,
    OrderItem,
)

if TYPE_CHECKING:
    from domain.entity import Product
    from repository.cart_repository import CartRepository
    from repository.order_repository import OrderRepository
    from repository.product_repository import ProductRepository


class ShopService:
    """
    EC サイトの注文・カート・商品操作を統合するサービス.

    Parameters
    ----------
    product_repo : ProductRepository
        商品リポジトリ。
    cart_repo : CartRepository
        カートリポジトリ。
    order_repo : OrderRepository
        注文リポジトリ。
    """

    def __init__(
        self,
        product_repo: ProductRepository,
        cart_repo: CartRepository,
        order_repo: OrderRepository,
    ) -> None:
        self.product_repo = product_repo
        self.cart_repo = cart_repo
        self.order_repo = order_repo

    def get_products_list(self) -> list[Product]:
        """
        全ての商品情報を取得する.

        Returns
        -------
        list[Product]
            商品エンティティのリスト。
        """
        return self.product_repo.find_all()

    def add_item_to_cart(
        self, user_id: str, product_id: str, quantity: int
    ) -> None:
        """
        カートに商品を追加するビジネスロジック.

        商品の存在チェックと在庫チェックを行い、
        カートエンティティを更新して保存します。

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
        product = self.product_repo.find_by_id(product_id)
        if product is None:
            msg = f"エラー: 商品 {product_id} が見つかりません"
            raise ValueError(msg)

        if not product.has_enough_stock(quantity):
            msg = (
                f"エラー: {product.name} の在庫が不足しています"
                f"(残り {product.stock}個)"
            )
            raise ValueError(msg)

        cart = self.cart_repo.get_or_create(user_id)
        cart.add_item(product_id, quantity)
        self.cart_repo.save(cart)

    def remove_item_from_cart(self, user_id: str, product_id: str) -> None:
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
            カートが存在しないか空の場合、または商品がカートに存在しない場合。
        """
        cart = self.cart_repo.find_by_user_id(user_id)
        if cart is None or cart.is_empty:
            msg = "エラー: カートが空です"
            raise ValueError(msg)

        cart.remove_item(product_id)
        self.cart_repo.save(cart)

    def get_cart_details(self, user_id: str) -> CartDetails | None:
        """
        カートの詳細情報と計算結果 (小計、消費税、合計) を取得する.

        Parameters
        ----------
        user_id : str
            ユーザーID。

        Returns
        -------
        CartDetails | None
            カート内の商品詳細と合計金額。カートが存在しないか空の場合は None。
        """
        cart = self.cart_repo.find_by_user_id(user_id)
        if cart is None or cart.is_empty:
            return None

        subtotal = 0
        items: list[CartDetailItem] = []
        for cart_item in cart.items:
            product = self.product_repo.find_by_id(cart_item.product_id)
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

    def place_order(self, user_id: str) -> Order:
        """
        注文を確定するビジネスロジック.

        在庫チェック・注文作成・在庫減少・カートクリアを行い、注文エンティティを保存します。

        Parameters
        ----------
        user_id : str
            ユーザーID。

        Returns
        -------
        Order
            作成・保存された注文エンティティ。

        Raises
        ------
        ValueError
            カートが存在しないか空の場合、または在庫が不足している場合。
        """
        cart = self.cart_repo.find_by_user_id(user_id)
        if cart is None or cart.is_empty:
            msg = "エラー: カートが空です"
            raise ValueError(msg)

        # 1. 在庫チェック
        for cart_item in cart.items:
            product = self.product_repo.find_by_id(cart_item.product_id)
            if product is None:
                msg = f"エラー: 商品 {cart_item.product_id} が見つかりません"
                raise ValueError(msg)

            if not product.has_enough_stock(cart_item.quantity):
                msg = (
                    f"エラー: {product.name} の在庫が不足しています"
                    f"(残り {product.stock}個)"
                )
                raise ValueError(msg)

        # 2. 注文明細アイテムの作成
        order_items: list[OrderItem] = []
        for cart_item in cart.items:
            product = self.product_repo.find_by_id(cart_item.product_id)
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

        # 3. 注文エンティティの作成 (ドメインファクトリに計算を委譲)
        order_id = self.order_repo.next_order_id()
        order = Order.create(
            order_id=order_id,
            user_id=user_id,
            items=order_items,
        )

        # 4. 注文の永続化
        self.order_repo.save(order)

        # 5. 在庫の減少と更新
        for cart_item in cart.items:
            product = self.product_repo.find_by_id(cart_item.product_id)
            if product is not None:
                product.decrease_stock(cart_item.quantity)
                self.product_repo.save(product)

        # 6. カートのクリアと永続化
        cart.clear()
        self.cart_repo.save(cart)

        return order

    def get_order_history(self, user_id: str) -> list[Order]:
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
        return self.order_repo.find_by_user_id(user_id)
