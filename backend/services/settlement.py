def compute_settlements(
    balances: dict[str, float],
    eps: float = 1e-6,
) -> list[tuple[str, str, float]]:
    creditors = [(uid, bal) for uid, bal in balances.items() if bal > eps]
    debtors = [(uid, -bal) for uid, bal in balances.items() if bal < -eps]

    creditors.sort(key=lambda x: x[1], reverse=True)
    debtors.sort(key=lambda x: x[1], reverse=True)

    transfers: list[tuple[str, str, float]] = []

    i = 0
    j = 0

    while i < len(debtors) and j < len(creditors):
        deb_id, deb_amt = debtors[i]
        cred_id, cred_amt = creditors[j]

        pay = min(deb_amt, cred_amt)
        if pay <= eps:
            break

        transfers.append((deb_id, cred_id, round(pay, 2)))

        deb_amt -= pay
        cred_amt -= pay

        if deb_amt <= eps:
            i += 1
        else:
            debtors[i] = (deb_id, deb_amt)

        if cred_amt <= eps:
            j += 1
        else:
            creditors[j] = (cred_id, cred_amt)

    return transfers
