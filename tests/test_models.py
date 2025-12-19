from backend.models.currency import Currency
from backend.models.expense import Expense
from backend.models.tricount import Tricount
from backend.models.user import User


def test_create_tricount():
    """Test creating a tricount."""
    tricount = Tricount(name="Test Tricount", currency=Currency.EUR)
    assert tricount.name == "Test Tricount"
    assert tricount.currency == Currency.EUR
    assert len(tricount.users) == 0
    assert len(tricount.expenses) == 0
    assert tricount.id is not None


def test_add_user_to_tricount():
    """Test adding a user to tricount."""
    tricount = Tricount(name="Test")
    user = tricount.add_user("Hamza", "auth123")

    assert user.name == "Hamza"
    assert user.auth_id == "auth123"
    assert len(tricount.users) == 1
    assert tricount.users[0] == user


def test_get_user():
    """Test getting a user from tricount."""
    tricount = Tricount(name="Test")
    user = tricount.add_user("Audric", "auth456")

    found_user = tricount.get_user(user.id)
    assert found_user == user

    not_found = tricount.get_user("nonexistent")
    assert not_found is None


def test_modify_user_auth_id():
    """Test modifying user auth_id."""
    tricount = Tricount(name="Test")
    user = tricount.add_user("Zak", "old_auth")

    modified = tricount.modify_user_auth_id(user.id, "new_auth")
    assert modified.auth_id == "new_auth"

    not_found = tricount.modify_user_auth_id("nonexistent", "auth")
    assert not_found is None


def test_add_expense_to_tricount():
    """Test adding an expense."""
    tricount = Tricount(name="Test")
    user1 = tricount.add_user("Vincent", "auth1")
    user2 = tricount.add_user("Kouka", "auth2")

    tricount.add_expense(
        description="Lunch",
        amount=50.0,
        payer_id=user1.id,
        participants_ids=[user1.id, user2.id],
    )

    assert len(tricount.expenses) == 1
    expense = tricount.expenses[0]
    assert expense.description == "Lunch"
    assert expense.amount == 50.0
    assert expense.payer_id == user1.id
    assert len(expense.participants_ids) == 2


def test_expense_split_amount():
    """Test expense split calculation."""
    expense = Expense(
        description="Test",
        amount=100.0,
        payer_id="user1",
        participants_ids=["user1", "user2", "user3", "user4"],
    )

    split = expense.split_amount()
    assert split == 25.0


def test_expense_split_amount_no_participants():
    """Test expense split with no participants."""
    expense = Expense(
        description="Test", amount=100.0, payer_id="user1", participants_ids=[]
    )

    split = expense.split_amount()
    assert split == 0.0


def test_user_str():
    """Test user string representation."""
    user = User(name="Alice")
    assert "Alice" in str(user)
    assert user.id in str(user)
