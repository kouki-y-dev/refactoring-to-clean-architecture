"""ドメインエンティティ定義.

EC サイトの注文システムにおけるドメインモデルを定義するモジュール。
Pydantic BaseModel を使用し、型安全性とバリデーションを提供します。
"""

from datetime import datetime

from pydantic import BaseModel, Field

TAX_RATE = 0.10


# ---------------------------------------------------------------------------
# 商品
# ---------------------------------------------------------------------------


class Product(BaseModel):
    """商品エンティティ.

    Attributes
    ----------
    id : str
        商品ID。
    name : str
        商品名。
    price : int
        商品価格 (0以上) 。
    stock : int
        在庫数 (0以上) 。
    """

    id: str
    name: str
    price: int = Field(ge=0)
    stock: int = Field(ge=0)

    def has_enough_stock(self, quantity: int) -> bool:
        """指定された数量の在庫があるかチェックする.

        Parameters
        ----------
        quantity : int
            要求数量。

        Returns
        -------
        bool
            在庫が十分な場合は True。
        """
        return self.stock >= quantity

    def decrease_stock(self, quantity: int) -> None:
        """在庫を減少させる.

        Parameters
        ----------
        quantity : int
            減少させる数量。

        Raises
        ------
        ValueError
            在庫が不足している場合。
        """
        if not self.has_enough_stock(quantity):
            msg = (
                f"エラー: {self.name} の在庫が不足しています"
                f"(残り {self.stock}個)"
            )
            raise ValueError(msg)
        self.stock -= quantity


# ---------------------------------------------------------------------------
# カートアイテム / カート
# ---------------------------------------------------------------------------


class CartItem(BaseModel):
    """カートアイテム.

    Attributes
    ----------
    product_id : str
        商品ID。
    quantity : int
        数量 (1以上) 。
    """

    product_id: str
    quantity: int = Field(gt=0)


class Cart(BaseModel):
    """カートエンティティ.

    Attributes
    ----------
    user_id : str
        ユーザーID。
    items : list[CartItem]
        カート内のアイテムリスト。
    """

    user_id: str
    items: list[CartItem] = Field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        """カートが空かどうかを返す."""
        return len(self.items) == 0

    def add_item(self, product_id: str, quantity: int) -> None:
        """カートに商品を追加する.

        既にカートにある商品の場合は数量を加算する。

        Parameters
        ----------
        product_id : str
            追加する商品のID。
        quantity : int
            追加する数量。
        """
        for item in self.items:
            if item.product_id == product_id:
                item.quantity += quantity
                return
        self.items.append(CartItem(product_id=product_id, quantity=quantity))

    def remove_item(self, product_id: str) -> None:
        """カートから商品を削除する.

        Parameters
        ----------
        product_id : str
            削除する商品のID。

        Raises
        ------
        ValueError
            商品がカートに存在しない場合。
        """
        if not any(item.product_id == product_id for item in self.items):
            msg = f"エラー: 商品 {product_id} はカートにありません"
            raise ValueError(msg)
        self.items = [
            item for item in self.items if item.product_id != product_id
        ]

    def clear(self) -> None:
        """カートを空にする."""
        self.items = []


# ---------------------------------------------------------------------------
# カート詳細 (CartDetailItem / CartDetails) — 表示・集計用の値オブジェクト
# ---------------------------------------------------------------------------


class CartDetailItem(BaseModel, frozen=True):
    """カート詳細の個別アイテム.

    Attributes
    ----------
    product_id : str
        商品ID。
    name : str
        商品名。
    price : int
        単価 (0以上) 。
    quantity : int
        数量 (1以上) 。
    item_total : int
        小計 (price * quantity)  (0以上) 。
    """

    product_id: str
    name: str
    price: int = Field(ge=0)
    quantity: int = Field(gt=0)
    item_total: int = Field(ge=0)


class CartDetails(BaseModel, frozen=True):
    """カートの集計結果.

    Attributes
    ----------
    items : list[CartDetailItem]
        カート内の商品詳細リスト。
    subtotal : int
        小計 (税抜) 。
    tax : int
        消費税額。
    total : int
        合計金額 (税込) 。
    """

    items: list[CartDetailItem]
    subtotal: int = Field(ge=0)
    tax: int = Field(ge=0)
    total: int = Field(ge=0)


# ---------------------------------------------------------------------------
# 注文アイテム / 注文
# ---------------------------------------------------------------------------


class OrderItem(BaseModel, frozen=True):
    """注文明細アイテム.

    Attributes
    ----------
    product_id : str
        商品ID。
    name : str
        商品名。
    price : int
        単価 (0以上) 。
    quantity : int
        数量 (1以上) 。
    subtotal : int
        小計 (price * quantity)  (0以上) 。
    """

    product_id: str
    name: str
    price: int = Field(ge=0)
    quantity: int = Field(gt=0)
    subtotal: int = Field(ge=0)


class Order(BaseModel, frozen=True):
    """注文エンティティ.

    Attributes
    ----------
    order_id : str
        注文ID。
    user_id : str
        ユーザーID。
    items : list[OrderItem]
        注文明細リスト。
    subtotal : int
        小計 (税抜) 。
    tax : int
        消費税額。
    total : int
        合計金額 (税込) 。
    created_at : datetime
        注文作成日時。
    """

    order_id: str
    user_id: str
    items: list[OrderItem]
    subtotal: int = Field(ge=0)
    tax: int = Field(ge=0)
    total: int = Field(ge=0)
    created_at: datetime

    @classmethod
    def create(
        cls,
        order_id: str,
        user_id: str,
        items: list[OrderItem],
        *,
        created_at: datetime | None = None,
    ) -> Order:
        """ドメインルールに基づいて注文を生成する.

        小計・消費税 (10%) ・合計金額を自動計算します。

        Parameters
        ----------
        order_id : str
            注文ID。
        user_id : str
            ユーザーID。
        items : list[OrderItem]
            注文明細リスト。
        created_at : datetime | None, optional
            注文日時。省略時は現在時刻を使用。

        Returns
        -------
        Order
            生成された注文エンティティ。
        """
        if created_at is None:
            created_at = datetime.now()  # noqa: DTZ005

        subtotal = sum(item.subtotal for item in items)
        tax = int(subtotal * TAX_RATE)
        total = subtotal + tax

        return cls(
            order_id=order_id,
            user_id=user_id,
            items=items,
            subtotal=subtotal,
            tax=tax,
            total=total,
            created_at=created_at,
        )
