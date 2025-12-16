from backend.models.tricount import Tricount


def compute_balances(tricount: Tricount) -> dict[str, float]:
    balances: dict[str, float] = {user.id: 0.0 for user in tricount.users}

    for expense in tricount.expenses:
        if not expense.participants_ids:
            continue

        amount = float(expense.amount)

        if expense.payer_id in balances:
            balances[expense.payer_id] += amount

        if expense.weights:
            total_weight = sum(expense.weights.values())

            if total_weight > 0:
                for uid, weight in expense.weights.items():
                    if uid in balances:
                        share = (weight / total_weight) * amount
                        balances[uid] -= share

            continue

        count = len(expense.participants_ids)
        if count > 0:
            share = amount / count
            for participant_id in expense.participants_ids:
                if participant_id in balances:
                    balances[participant_id] -= share

    return balances
