from backend.models.tricount import Tricount


def compute_balances(tricount: Tricount) -> dict[str, float]:

    balances: dict[str, float] = {user.id: 0.0 for user in tricount.users}

    for expense in tricount.expenses:
        if not expense.participants_ids:
            continue

        share = expense.split_amount()

        balances[expense.payer_id] += expense.amount

        for participant_id in expense.participants_ids:
            balances[participant_id] -= share

    return balances
