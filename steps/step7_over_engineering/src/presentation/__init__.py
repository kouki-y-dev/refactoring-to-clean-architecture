"""Presentation layer for Step 7 (Over Engineering).

Interface Adapters レイヤーにおける
Controller, Presenter, ViewModel, CLI を提供します。
"""

from presentation.cli import CLI
from presentation.controller import OrderController
from presentation.presenter import (
    AddToCartPresenter,
    GetOrderHistoryPresenter,
    ListProductsPresenter,
    PlaceOrderPresenter,
    RemoveFromCartPresenter,
    ViewCartPresenter,
)
from presentation.view_model import (
    AddToCartViewModel,
    GetOrderHistoryViewModel,
    ListProductsViewModel,
    OrderHistoryItemViewModel,
    PlaceOrderItemViewModel,
    PlaceOrderViewModel,
    ProductItemViewModel,
    RemoveFromCartViewModel,
    ViewCartItemViewModel,
    ViewCartViewModel,
)

__all__ = [
    "CLI",
    "AddToCartPresenter",
    "AddToCartViewModel",
    "GetOrderHistoryPresenter",
    "GetOrderHistoryViewModel",
    "ListProductsPresenter",
    "ListProductsViewModel",
    "OrderController",
    "OrderHistoryItemViewModel",
    "PlaceOrderItemViewModel",
    "PlaceOrderPresenter",
    "PlaceOrderViewModel",
    "ProductItemViewModel",
    "RemoveFromCartPresenter",
    "RemoveFromCartViewModel",
    "ViewCartItemViewModel",
    "ViewCartPresenter",
    "ViewCartViewModel",
]
