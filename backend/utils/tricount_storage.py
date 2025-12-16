import json
from pathlib import Path

from backend.models.currency import Currency
from backend.models.expense import Expense
from backend.models.tricount import Tricount
from backend.models.user import User

DATA_FILE = Path("data/tricounts.json")


def tricount_to_dict(tricount: Tricount) -> dict:
    return {
        "id": tricount.id,
        "name": tricount.name,
        "currency": tricount.currency.value,
        "users": [
            {
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "auth_id": u.auth_id,
            }
            for u in tricount.users
        ],
        "expenses": [
            {
                "id": e.id,
                "description": e.description,
                "amount": e.amount,
                "currency": e.currency.value,
                "payer_id": e.payer_id,
                "participants_ids": e.participants_ids,
                "weights": e.weights,
            }
            for e in tricount.expenses
        ],
    }


def tricount_from_dict(data: dict) -> Tricount:
    tricount = Tricount(
        id=data["id"],
        name=data["name"],
        currency=Currency(data["currency"]),
    )

    for u in data.get("users", []):
        user = User(
            id=u["id"],
            name=u["name"],
            email=u.get("email"),
            auth_id=u.get("auth_id"),
        )
        tricount.users.append(user)

    for e in data.get("expenses", []):
        expense = Expense(
            id=e["id"],
            description=e["description"],
            amount=e["amount"],
            currency=Currency(e["currency"]),
            payer_id=e["payer_id"],
            participants_ids=e["participants_ids"],
            weights=e.get("weights", {}),
        )
        tricount.expenses.append(expense)

    return tricount


def save_tricounts(tricounts: list[Tricount]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = [tricount_to_dict(t) for t in tricounts]
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_tricounts() -> list[Tricount]:
    if not DATA_FILE.exists() or DATA_FILE.stat().st_size == 0:
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            raw = json.load(f)
    except json.JSONDecodeError:
        return []
    return [tricount_from_dict(t) for t in raw]
