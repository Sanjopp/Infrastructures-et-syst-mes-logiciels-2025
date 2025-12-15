from io import BytesIO

from openpyxl import Workbook

from backend.models.tricount import Tricount
from backend.services.balance import compute_balances
from backend.services.settlement import compute_settlements


def export_tricount_to_excel(tricount: Tricount) -> BytesIO:
    """
    Exporte un Tricount en fichier Excel (en mémoire).

    Feuilles:
      - Expenses: description, amount, currency, payer, participants
      - Balances: user, balance
      - Settlements: from, to, amount

    Retour: BytesIO prêt à être envoyé par Flask (send_file).
    """
    wb = Workbook()

    # Expenses
    ws_exp = wb.active
    ws_exp.title = "Expenses"
    ws_exp.append(["Description", "Amount", "Currency", "Payer", "Participants"])

    for expense in tricount.expenses:
        payer_name = ""

        for user in tricount.users:
            if user.id == expense.payer_id:
                payer_name = user.name
                break

        participant_names = []

        for user in tricount.users:
            if user.id in expense.participants_ids:
                participant_names.append(user.name)


        ws_exp.append(
            [
                expense.description,
                expense.amount,
                expense.currency.value,
                payer_name,
                ", ".join(participant_names),
            ]
        )

    # Balances
    ws_bal = wb.create_sheet(title="Balances")
    ws_bal.append(["User", "Balance"])

    balances = compute_balances(tricount)
    for user in tricount.users:
        ws_bal.append([user.name, round(balances.get(user.id, 0.0), 2)])

    # Settlements
    ws_set = wb.create_sheet(title="Settlements")
    ws_set.append(["From", "To", "Amount"])

    settlements = compute_settlements(balances)
    for from_id, to_id, amount in settlements:
        from_name = ""
        to_name = ""

        for user in tricount.users:
            if user.id == from_id:
                from_name = user.name
            if user.id == to_id:
                to_name = user.name

        ws_set.append([from_name, to_name, amount])


    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output
