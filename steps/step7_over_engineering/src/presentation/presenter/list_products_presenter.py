"""商品一覧取得プレゼンターの実装."""

from usecase.port.list_products_port import (
    ListProductsOutputPort,
    ListProductsResponseDTO,
)

from presentation.view_model.models import (
    ListProductsViewModel,
    ProductItemViewModel,
)


class ListProductsPresenter(ListProductsOutputPort):
    """商品一覧出力境界の実装プレゼンター."""

    def __init__(self) -> None:
        self.view_model: ListProductsViewModel = ListProductsViewModel()

    def present_success(self, response: ListProductsResponseDTO) -> None:
        """成功結果を ViewModel に変換・設定する.

        Parameters
        ----------
        response : ListProductsResponseDTO
            レスポンス DTO。
        """
        items = [
            ProductItemViewModel(
                product_id=p.product_id,
                name=p.name,
                price_display=f"¥{p.price}",
                stock_display=str(p.stock),
            )
            for p in response.products
        ]
        self.view_model = ListProductsViewModel(
            is_success=True, products=items
        )

    def present_error(self, error_message: str) -> None:
        """エラー結果を ViewModel に設定する.

        Parameters
        ----------
        error_message : str
            エラーメッセージ。
        """
        self.view_model = ListProductsViewModel(
            is_success=False,
            error_message=error_message,
        )
