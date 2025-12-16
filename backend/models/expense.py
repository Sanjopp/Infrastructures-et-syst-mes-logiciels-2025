from dataclasses import dataclass, field
from uuid import uuid4

from .currency import Currency


@dataclass
class Expense:
    id: str = field(default_factory=lambda: str(uuid4()))
    description: str = ""
    amount: float = 0.0
    currency: Currency = Currency.EUR

    payer_id: str = ""
    participants_ids: list[str] = field(default_factory=list)
    weights: dict[str, float] = field(default_factory=dict)

    def split_amount(self) -> float:
        if not self.participants_ids:
            return 0.0
        return self.amount / len(self.participants_ids)
