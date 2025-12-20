from backend.models.currency import Currency
from backend.models.expense import Expense
from backend.models.tricount import Tricount
from backend.models.user import User


def test_create_tricount():
    tricount = Tricount(name="Tricount", currency=Currency.EUR)
    assert tricount.name == "Tricount"
    assert tricount.currency == Currency.EUR
    assert len(tricount.users) == 0
    assert len(tricount.expenses) == 0
    assert tricount.id is not None


def test_add_user_to_tricount():
    tricount = Tricount(name="Tricount", currency=Currency.EUR)
    user = tricount.add_user("User", "user@test.com")

    assert user.name == "User"
    assert user.email == "user@test.com"
    assert len(tricount.users) == 1
    assert tricount.users[0] == user


def test_get_user():
    tricount = Tricount(name="Tricount", currency=Currency.EUR)
    user = tricount.add_user("User", "user@test.com")

    found_user = tricount.get_user(user.id)
    assert found_user == user

    not_found = tricount.get_user("nonexistent")
    assert not_found is None


def test_modify_user_email():
    tricount = Tricount(name="Tricount", currency=Currency.EUR)
    user = tricount.add_user("User", "user@test.com")

    modified = tricount.modify_user_email(user.id, "newuser@test.com")
    assert modified.email == "newuser@test.com"

    not_found = tricount.modify_user_email("nonexistent", "newuser@test.com")
    assert not_found is None


def test_add_expense_to_tricount():
    tricount = Tricount(name="Tricount", currency=Currency.EUR)
    user1 = tricount.add_user("User1", "user1@test.com")
    user2 = tricount.add_user("User2", "user2@test.com")

    tricount.add_expense(
        description="Expense",
        amount=50.0,
        payer_id=user1.id,
        participants_ids=[user1.id, user2.id],
    )

    assert len(tricount.expenses) == 1
    expense = tricount.expenses[0]
    assert expense.description == "Expense"
    assert expense.amount == 50.0
    assert expense.payer_id == user1.id
    assert len(expense.participants_ids) == 2


def test_expense_split_amount():
    expense = Expense(
        description="Expense",
        amount=100.0,
        payer_id="User1",
        participants_ids=["User1", "User2", "User3", "User4"],
    )

    split = expense.split_amount()
    assert split == 25.0


def test_expense_split_amount_no_participants():
    expense = Expense(
        description="Expense",
        amount=100.0,
        payer_id="User1",
        participants_ids=[],
    )

    split = expense.split_amount()
    assert split == 0.0
