"""永続化ストレージ用データモデル (Persistence Records) .

クリーンアーキテクチャの Gateways & Persistence レイヤーにおいて、
ストレージ (DB やオンメモリテーブル) に格納されるデータ構造です。
ドメインエンティティとは厳格に分離されています。
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


@dataclass
class ProductRecord:
    """商品テーブル/ストレージ用レコード.

    Attributes
    ----------
    id : str
        商品ID。
    name : str
        商品名。
    price : int
        商品価格。
    stock : int
        在庫数。
    """

    id: str
    name: str
    price: int
    stock: int


@dataclass
class CartItemRecord:
    """カートアイテムテーブル/ストレージ用レコード.

    Attributes
    ----------
    product_id : str
        商品ID。
    quantity : int
        数量。
    """

    product_id: str
    quantity: int


@dataclass
class CartRecord:
    """カートテーブル/ストレージ用レコード.

    Attributes
    ----------
    user_id : str
        ユーザーID。
    items : list[CartItemRecord]
        カート内アイテムリスト。
    """

    user_id: str
    items: list[CartItemRecord] = field(default_factory=list)


@dataclass
class OrderItemRecord:
    """注文明細テーブル/ストレージ用レコード.

    Attributes
    ----------
    product_id : str
        商品ID。
    name : str
        商品名。
    price : int
        単価。
    quantity : int
        数量。
    subtotal : int
        小計。
    """

    product_id: str
    name: str
    price: int
    quantity: int
    subtotal: int


@dataclass
class OrderRecord:
    """注文テーブル/ストレージ用レコード.

    Attributes
    ----------
    order_id : str
        注文ID。
    user_id : str
        ユーザーID。
    items : list[OrderItemRecord]
        明細レコードリスト。
    subtotal : int
        小計。
    tax : int
        消費税額。
    total : int
        合計金額。
    created_at : datetime
        作成日時。
    """

    order_id: str
    user_id: str
    items: list[OrderItemRecord]
    subtotal: int
    tax: int
    total: int
    created_at: datetime
