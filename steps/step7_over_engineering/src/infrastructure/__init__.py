"""Infrastructure layer for Step 7 (Over Engineering).

Frameworks & Drivers / Gateways レイヤーにおける
永続化モデル、データマッパー、具象ゲートウェイを提供します。
"""

from infrastructure.gateway import (
    INITIAL_PRODUCTS,
    InMemoryCartGateway,
    InMemoryOrderGateway,
    InMemoryProductGateway,
)
from infrastructure.mapper.data_mapper import (
    CartDataMapper,
    OrderDataMapper,
    ProductDataMapper,
)
from infrastructure.persistence.models import (
    CartItemRecord,
    CartRecord,
    OrderItemRecord,
    OrderRecord,
    ProductRecord,
)

__all__ = [
    "INITIAL_PRODUCTS",
    "CartDataMapper",
    "CartItemRecord",
    "CartRecord",
    "InMemoryCartGateway",
    "InMemoryOrderGateway",
    "InMemoryProductGateway",
    "OrderDataMapper",
    "OrderItemRecord",
    "OrderRecord",
    "ProductDataMapper",
    "ProductRecord",
]
