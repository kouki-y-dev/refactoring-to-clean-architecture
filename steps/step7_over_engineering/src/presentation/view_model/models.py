"""プレゼンテーション層の View Model 定義.

UI (CLI / Web 等) の画面表示に最適化されたデータ構造です。
通貨フォーマットや成功・失敗フラグ、表示用メッセージなどを保持します。
"""

from dataclasses import dataclass, field


@dataclass
class ProductItemViewModel:
    """商品一覧の個別表示モデル."""

    product_id: str
    name: str
    price_display: str  # 例: "¥100,000"
    stock_display: str  # 例: "5"


@dataclass
class ListProductsViewModel:
    """商品一覧画面の View Model."""

    is_success: bool = True
    error_message: str = ""
    products: list[ProductItemViewModel] = field(default_factory=list)


@dataclass
class AddToCartViewModel:
    """カート追加結果の View Model."""

    is_success: bool = True
    message: str = ""
    error_message: str = ""


@dataclass
class RemoveFromCartViewModel:
    """カート削除結果の View Model."""

    is_success: bool = True
    message: str = ""
    error_message: str = ""


@dataclass
class ViewCartItemViewModel:
    """カート内明細行の表示モデル."""

    name: str
    quantity_display: str
    total_display: str  # 例: "¥6,000"


@dataclass
class ViewCartViewModel:
    """カート表示画面の View Model."""

    is_success: bool = True
    is_empty: bool = True
    user_id: str = ""
    items: list[ViewCartItemViewModel] = field(default_factory=list)
    subtotal_display: str = ""
    tax_display: str = ""
    total_display: str = ""
    error_message: str = ""


@dataclass
class PlaceOrderItemViewModel:
    """注文確定明細行の表示モデル."""

    name: str
    quantity: int
    subtotal_display: str


@dataclass
class PlaceOrderViewModel:
    """注文確定結果の View Model."""

    is_success: bool = True
    order_id: str = ""
    total_display: str = ""
    error_message: str = ""


@dataclass
class OrderHistoryItemViewModel:
    """注文履歴明細行の表示モデル."""

    order_id: str
    created_at_display: str
    total_display: str
    items: list[PlaceOrderItemViewModel] = field(default_factory=list)


@dataclass
class GetOrderHistoryViewModel:
    """注文履歴一覧画面の View Model."""

    is_success: bool = True
    user_id: str = ""
    orders: list[OrderHistoryItemViewModel] = field(default_factory=list)
    error_message: str = ""
