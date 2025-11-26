from dataclasses import dataclass, field
from uuid import uuid4

from .currency import Currency
from .expense import Expense
from .user import User


@dataclass
class Tricount:
    id: str = field(default_factory=lambda: str(uuid4()))
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
    ) -> Expense:
        expense = Expense(
            description=description,
            amount=amount,
            payer_id=payer_id,
            participants_ids=participants_ids,
            currency=self.currency,
        )
        self.expenses.append(expense)
        return expense

    def get_user(self, user_id: str) -> User | None:
        return next((u for u in self.users if u.id == user_id), None)
