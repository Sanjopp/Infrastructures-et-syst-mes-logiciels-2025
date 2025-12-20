from backend.models.currency import Currency
from backend.models.tricount import Tricount
from backend.services.balance import compute_balances
from backend.services.settlement import compute_settlements


def test_compute_balances_simple():
    tricount = Tricount(name="Tricount", currency=Currency.EUR)
    user1 = tricount.add_user("User1", "user1@test.com")
    user2 = tricount.add_user("User2", "user2@test.com")

    tricount.add_expense(
        description="Expense",
        amount=100.0,
        payer_id=user1.id,
        participants_ids=[user1.id, user2.id],
    )

    balances = compute_balances(tricount)

    assert balances[user1.id] == 50.0
    assert balances[user2.id] == -50.0


def test_compute_balances_multiple_expenses():
    tricount = Tricount(name="Tricount", currency=Currency.EUR)
    user1 = tricount.add_user("User1", "user1@test.com")
    user2 = tricount.add_user("User2", "user2@test.com")

    tricount.add_expense(
        description="Expense 1",
        amount=90.0,
        payer_id=user1.id,
        participants_ids=[user1.id, user2.id],
    )

    tricount.add_expense(
        description="Expense 2",
        amount=60.0,
        payer_id=user2.id,
        participants_ids=[user1.id, user2.id],
    )

    balances = compute_balances(tricount)

    assert balances[user1.id] == 15.0
    assert balances[user2.id] == -15.0


def test_compute_balances_with_weights():
    tricount = Tricount(name="Tricount", currency=Currency.EUR)
    user1 = tricount.add_user("User1", "user1@test.com")
    user2 = tricount.add_user("User2", "user2@test.com")
    user3 = tricount.add_user("User3", "user3@test.com")

    tricount.add_expense(
        description="Weighted Expense",
        amount=120.0,
        payer_id=user1.id,
        participants_ids=[user1.id, user2.id, user3.id],
        weights={user1.id: 1.0, user2.id: 2.0, user3.id: 3.0},
    )

    balances = compute_balances(tricount)

    assert balances[user1.id] == 100.0
    assert balances[user2.id] == -40.0
    assert balances[user3.id] == -60.0


def test_compute_settlements_simple():
    balances = {
        "User1": 50.0,
        "User2": -50.0,
    }

    settlements = compute_settlements(balances)

    assert len(settlements) == 1
    assert settlements[0] == ("User2", "User1", 50.0)


def test_compute_settlements_multiple():
    balances = {"User1": 60.0, "User2": -30.0, "User3": -30.0}
    settlements = compute_settlements(balances)

    assert len(settlements) == 2
    assert ("User2", "User1", 30.0) in settlements
    assert ("User3", "User1", 30.0) in settlements


def test_compute_settlements_complex():
    balances = {"User1": 100.0, "User2": 50.0, "User3": -80.0, "User4": -70.0}

    settlements = compute_settlements(balances)

    # Verify total amounts
    total_paid = sum(amount for _, _, amount in settlements)
    total_owed = sum(-bal for bal in balances.values() if bal < 0)
    assert abs(total_paid - total_owed) < 0.01

    # Verify all debts are from debtors to creditors
    for debtor, creditor, amount in settlements:
        assert balances[debtor] < 0
        assert balances[creditor] > 0


def test_compute_settlements_balanced():
    balances = {"User1": 0.0, "User2": 0.0, "User3": 0.0}

    settlements = compute_settlements(balances)
    assert len(settlements) == 0
