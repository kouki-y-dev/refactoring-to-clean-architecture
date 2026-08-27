"""Step 6: インフラストラクチャ層単体テスト.

InMemoryProductRepository, InMemoryCartRepository, InMemoryOrderRepository の
保存、取得、検索、削除、初期化などの振る舞い、
およびドメイン層の抽象基底クラス (IProductRepository 等) を
正しく実装しているかを検証します。
"""

from datetime import UTC, datetime

from domain.entity import Cart, Order, OrderItem, Product
from domain.repository import (
    ICartRepository,
    IOrderRepository,
    IProductRepository,
)
from infrastructure.repository.cart_repository import (
    CartRepository,
    InMemoryCartRepository,
)
from infrastructure.repository.order_repository import (
    InMemoryOrderRepository,
    OrderRepository,
)
from infrastructure.repository.product_repository import (
    InMemoryProductRepository,
    ProductRepository,
)

# -------------------------------------------------------------------
# 商品リポジトリのテスト
# -------------------------------------------------------------------


class TestProductRepository:
    """ProductRepository のテスト."""

    def test_implements_interface(self) -> None:
        """IProductRepository インターフェースを実装していること."""
        repo = InMemoryProductRepository()
        assert isinstance(repo, IProductRepository)

    def test_default_initialization(self) -> None:
        """デフォルト初期化で3件の商品が読み込まれること."""
        repo = ProductRepository()
        products = repo.find_all()
        assert len(products) == 3
        ids = [p.id for p in products]
        assert "P001" in ids
        assert "P002" in ids
        assert "P003" in ids

    def test_custom_initialization(self) -> None:
        """カスタム商品データで初期化できること."""
        custom = {
            "P100": Product(id="P100", name="ノート", price=300, stock=50),
        }
        repo = ProductRepository(products=custom)
        assert len(repo.find_all()) == 1
        assert repo.find_by_id("P100") is not None

    def test_find_by_id_exists(
        self, product_repo: InMemoryProductRepository
    ) -> None:
        """存在する商品IDで商品が取得できること."""
        product = product_repo.find_by_id("P001")
        assert product is not None
        assert product.name == "Tシャツ"
        assert product.price == 2000

    def test_find_by_id_not_exists(
        self, product_repo: InMemoryProductRepository
    ) -> None:
        """存在しない商品IDで None が返ること."""
        assert product_repo.find_by_id("NONEXISTENT") is None

    def test_save_new_product(
        self, product_repo: InMemoryProductRepository
    ) -> None:
        """新規商品が保存されること."""
        new_prod = Product(id="P004", name="タオル", price=800, stock=15)
        product_repo.save(new_prod)
        assert product_repo.find_by_id("P004") == new_prod
        assert len(product_repo.find_all()) == 4

    def test_save_update_existing_product(
        self, product_repo: InMemoryProductRepository
    ) -> None:
        """既存商品が更新保存されること."""
        product = product_repo.find_by_id("P001")
        assert product is not None
        product.stock = 5
        product_repo.save(product)
        updated = product_repo.find_by_id("P001")
        assert updated is not None
        assert updated.stock == 5


# -------------------------------------------------------------------
# カートリポジトリのテスト
# -------------------------------------------------------------------


class TestCartRepository:
    """CartRepository のテスト."""

    def test_implements_interface(self) -> None:
        """ICartRepository インターフェースを実装していること."""
        repo = InMemoryCartRepository()
        assert isinstance(repo, ICartRepository)

    def test_empty_initialization(
        self, cart_repo: InMemoryCartRepository
    ) -> None:
        """初期状態でカートが存在しないこと."""
        assert cart_repo.find_by_user_id("user1") is None

    def test_custom_initialization(self) -> None:
        """初期データを指定して初期化できること."""
        cart = Cart(user_id="user_init")
        cart.add_item("P001", 1)
        repo = CartRepository(carts={"user_init": cart})
        found = repo.find_by_user_id("user_init")
        assert found is not None
        assert len(found.items) == 1

    def test_get_or_create_creates_new(
        self, cart_repo: InMemoryCartRepository
    ) -> None:
        """存在しないユーザーの場合、新しい空のカートが作成されること."""
        cart = cart_repo.get_or_create("user1")
        assert cart.user_id == "user1"
        assert cart.is_empty is True
        assert cart_repo.find_by_user_id("user1") is not None

    def test_get_or_create_returns_existing(
        self, cart_repo: InMemoryCartRepository
    ) -> None:
        """既存のカートがある場合、そのカートが返ること."""
        cart1 = cart_repo.get_or_create("user1")
        cart1.add_item("P001", 2)
        cart_repo.save(cart1)

        cart2 = cart_repo.get_or_create("user1")
        assert len(cart2.items) == 1
        assert cart2.items[0].product_id == "P001"
        assert cart2.items[0].quantity == 2

    def test_save_cart(self, cart_repo: InMemoryCartRepository) -> None:
        """カートを保存できること."""
        cart = Cart(user_id="user1")
        cart.add_item("P001", 3)
        cart_repo.save(cart)

        saved = cart_repo.find_by_user_id("user1")
        assert saved is not None
        assert saved.items[0].quantity == 3

    def test_delete_cart(self, cart_repo: InMemoryCartRepository) -> None:
        """カートを削除できること."""
        cart = cart_repo.get_or_create("user1")
        cart.add_item("P001", 1)
        cart_repo.save(cart)

        cart_repo.delete("user1")
        assert cart_repo.find_by_user_id("user1") is None

    def test_delete_nonexistent_cart(
        self, cart_repo: InMemoryCartRepository
    ) -> None:
        """存在しないカートを削除してもエラーにならないこと."""
        cart_repo.delete("nonexistent_user")


# -------------------------------------------------------------------
# 注文リポジトリのテスト
# -------------------------------------------------------------------


class TestOrderRepository:
    """OrderRepository のテスト."""

    def test_implements_interface(self) -> None:
        """IOrderRepository インターフェースを実装していること."""
        repo = InMemoryOrderRepository()
        assert isinstance(repo, IOrderRepository)

    def test_empty_initialization(
        self, order_repo: InMemoryOrderRepository
    ) -> None:
        """初期状態で注文が0件であること."""
        assert order_repo.count() == 0
        assert order_repo.find_all() == []

    def test_custom_initialization(self) -> None:
        """初期データを指定して初期化できること."""
        order = Order.create(
            order_id="ORD-0001",
            user_id="user1",
            items=[],
            created_at=datetime(2025, 1, 1, tzinfo=UTC),
        )
        repo = OrderRepository(orders={"ORD-0001": order})
        assert repo.count() == 1
        assert repo.find_by_id("ORD-0001") == order

    def test_save_and_find_by_id(
        self, order_repo: InMemoryOrderRepository
    ) -> None:
        """注文の保存とID検索ができること."""
        order = Order.create(
            order_id="ORD-0001",
            user_id="user1",
            items=[
                OrderItem(
                    product_id="P001",
                    name="Tシャツ",
                    price=2000,
                    quantity=1,
                    subtotal=2000,
                )
            ],
            created_at=datetime(2025, 1, 1, tzinfo=UTC),
        )
        order_repo.save(order)

        found = order_repo.find_by_id("ORD-0001")
        assert found == order
        assert order_repo.count() == 1

    def test_find_by_id_not_found(
        self, order_repo: InMemoryOrderRepository
    ) -> None:
        """存在しない注文IDで None が返ること."""
        assert order_repo.find_by_id("ORD-9999") is None

    def test_find_by_user_id(
        self, order_repo: InMemoryOrderRepository
    ) -> None:
        """ユーザーIDに紐づく注文のみが取得されること."""
        order1 = Order.create(
            order_id="ORD-0001",
            user_id="user1",
            items=[],
            created_at=datetime(2025, 1, 1, tzinfo=UTC),
        )
        order2 = Order.create(
            order_id="ORD-0002",
            user_id="user2",
            items=[],
            created_at=datetime(2025, 1, 2, tzinfo=UTC),
        )
        order3 = Order.create(
            order_id="ORD-0003",
            user_id="user1",
            items=[],
            created_at=datetime(2025, 1, 3, tzinfo=UTC),
        )
        order_repo.save(order1)
        order_repo.save(order2)
        order_repo.save(order3)

        user1_orders = order_repo.find_by_user_id("user1")
        assert len(user1_orders) == 2
        order_ids = [o.order_id for o in user1_orders]
        assert "ORD-0001" in order_ids
        assert "ORD-0003" in order_ids

        user2_orders = order_repo.find_by_user_id("user2")
        assert len(user2_orders) == 1
        assert user2_orders[0].order_id == "ORD-0002"

        user3_orders = order_repo.find_by_user_id("user3")
        assert user3_orders == []

    def test_next_order_id(self, order_repo: InMemoryOrderRepository) -> None:
        """注文IDの採番が正しく行われること."""
        assert order_repo.next_order_id() == "ORD-0001"

        order = Order.create(
            order_id="ORD-0001",
            user_id="user1",
            items=[],
            created_at=datetime(2025, 1, 1, tzinfo=UTC),
        )
        order_repo.save(order)

        assert order_repo.next_order_id() == "ORD-0002"
