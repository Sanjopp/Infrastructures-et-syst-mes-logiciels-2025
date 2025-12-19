from backend.models.currency import Currency
from backend.models.tricount import Tricount
from backend.services.balance import compute_balances
from backend.services.settlement import compute_settlements


def test_compute_balances_simple():
    """Test balance computation with simple expense."""
    tricount = Tricount(name="Test", currency=Currency.EUR)
    user1 = tricount.add_user("Dric", "auth1")
    user2 = tricount.add_user("Kouka", "auth2")

    # Dric pays 100 for both
    tricount.add_expense(
        description="Dinner",
        amount=100.0,
        payer_id=user1.id,
        participants_ids=[user1.id, user2.id],
    )

    balances = compute_balances(tricount)

    # Dric should be +50 (paid 100, owes 50)
    # Kouka should be -50 (paid 0, owes 50)
    assert balances[user1.id] == 50.0
    assert balances[user2.id] == -50.0


def test_compute_balances_multiple_expenses():
    """Test balance computation with multiple expenses."""
    tricount = Tricount(name="Test", currency=Currency.EUR)
    user1 = tricount.add_user("Dric", "auth1")
    user2 = tricount.add_user("Kouka", "auth2")

    # Dric pays 90
    tricount.add_expense(
        description="Expense 1",
        amount=90.0,
        payer_id=user1.id,
        participants_ids=[user1.id, user2.id],
    )

    # Bob pays 60
    tricount.add_expense(
        description="Expense 2",
        amount=60.0,
        payer_id=user2.id,
        participants_ids=[user1.id, user2.id],
    )

    balances = compute_balances(tricount)

    # Dric: paid 90, owes 75 (half of 150) = +15
    # Kouka: paid 60, owes 75 = -15
    assert balances[user1.id] == 15.0
    assert balances[user2.id] == -15.0


def test_compute_balances_with_weights():
    """Test balance computation with weighted expenses."""
    tricount = Tricount(name="Test", currency=Currency.EUR)
    user1 = tricount.add_user("Dric", "auth1")
    user2 = tricount.add_user("Kouka", "auth2")
    user3 = tricount.add_user("Zak", "auth3")

    # Dric pays 120, but weighted: Dric 1, Kouka 2, Zak 3
    tricount.add_expense(
        description="Weighted expense",
        amount=120.0,
        payer_id=user1.id,
        participants_ids=[user1.id, user2.id, user3.id],
        weights={user1.id: 1.0, user2.id: 2.0, user3.id: 3.0},
    )

    balances = compute_balances(tricount)

    # Total weight = 6
    # Dric: paid 120, owes 20 (1/6 of 120) = +100
    # Kouka: paid 0, owes 40 (2/6 of 120) = -40
    # Zak: paid 0, owes 60 (3/6 of 120) = -60
    assert balances[user1.id] == 100.0
    assert balances[user2.id] == -40.0
    assert balances[user3.id] == -60.0


def test_compute_settlements_simple():
    """Test settlement computation with simple case."""
    balances = {
        "user1": 50.0,  # Dric is owed 50
        "user2": -50.0,  # Kouka owes 50
    }

    settlements = compute_settlements(balances)

    assert len(settlements) == 1
    assert settlements[0] == ("user2", "user1", 50.0)


def test_compute_settlements_multiple():
    """Test settlement computation with multiple users."""
    balances = {"hamza": 60.0, "vincent": -30.0, "zak": -30.0}

    settlements = compute_settlements(balances)

    # Vincent and Zak should each pay Hamza 30
    assert len(settlements) == 2
    assert ("vincent", "hamza", 30.0) in settlements
    assert ("zak", "hamza", 30.0) in settlements


def test_compute_settlements_complex():
    """Test settlement computation with complex case."""
    balances = {"dric": 100.0, "kouka": 50.0, "zak": -80.0, "vincent": -70.0}

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
    """Test settlement when everyone is balanced."""
    balances = {"user1": 0.0, "user2": 0.0, "user3": 0.0}

    settlements = compute_settlements(balances)
    assert len(settlements) == 0
