from dataclasses import dataclass, field
from uuid import uuid4

from .currency import Currency
from .expense import Expense
from .user import User


@dataclass
class Tricount:
    id: str = field(default_factory=lambda: str(uuid4()))
    owner_auth_id: str = ""
    name: str = ""
    currency: Currency = Currency.EUR

    users: list[User] = field(default_factory=list)
    expenses: list[Expense] = field(default_factory=list)

    def add_user(self, name: str, email: str | None = None) -> User:
        user = User(name=name, email=email)
        self.users.append(user)
        return user

    def add_expense(
        self,
        description: str,
        amount: float,
        payer_id: str,
        participants_ids: list[str],
        weights: dict = None,
    ) -> Expense:
        if weights is None:
            weights = {}

        expense = Expense(
            id=str(uuid4()),
            description=description,
            amount=amount,
            currency=self.currency,
            payer_id=payer_id,
            participants_ids=participants_ids,
            weights=weights,
        )
        self.expenses.append(expense)

    def get_user(self, user_id: str) -> User | None:
        return next((u for u in self.users if u.id == user_id), None)
