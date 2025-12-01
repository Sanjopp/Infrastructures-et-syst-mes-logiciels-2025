from flask import Flask, jsonify, request
from flask_cors import CORS

from backend.models.currency import Currency
from backend.models.tricount import Tricount
from backend.services.balance import compute_balances
from backend.services.settlement import compute_settlements
from backend.utils.storage import load_tricounts, save_tricounts

app = Flask(__name__)
CORS(app)

tricounts = load_tricounts()


def find_tricount(tricount_id: str) -> Tricount | None:
    return next((t for t in tricounts if t.id == tricount_id), None)


def tricount_with_balances_to_dict(tricount: Tricount) -> dict:
    balances = compute_balances(tricount)
    settlements_raw = compute_settlements(balances)

    return {
        "id": tricount.id,
        "name": tricount.name,
        "currency": tricount.currency.value,
        "users": [
            {"id": u.id, "name": u.name, "email": u.email}
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
            }
            for e in tricount.expenses
        ],
        "balances": balances,
        "settlements": [
            {"from": f, "to": t, "amount": amount}
            for (f, t, amount) in settlements_raw
        ],
    }


@app.route("/")
def api_root():
    return jsonify({"status": "ok", "message": "Tricount API running"})


@app.route("/api/tricounts", methods=["GET"])
def api_list_tricounts():
    return jsonify(
        [
            {
                "id": t.id,
                "name": t.name,
                "currency": t.currency.value,
                "users_count": len(t.users),
                "expenses_count": len(t.expenses),
            }
            for t in tricounts
        ]
    )


@app.route("/api/tricounts", methods=["POST"])
def api_create_tricount():
    payload = request.get_json() or {}
    name = (payload.get("name") or "").strip()

    if not name:
        return jsonify({"error": "Name is required"}), 400

    t = Tricount(name=name, currency=Currency.EUR)
    tricounts.append(t)
    save_tricounts(tricounts)

    return jsonify(tricount_with_balances_to_dict(t)), 201


@app.route("/api/tricounts/<tricount_id>", methods=["GET"])
def api_get_tricount(tricount_id: str):
    t = find_tricount(tricount_id)
    if t is None:
        return jsonify({"error": "Not found"}), 404

    return jsonify(tricount_with_balances_to_dict(t))


@app.route("/api/tricounts/<tricount_id>/users", methods=["POST"])
def api_add_user(tricount_id: str):
    t = find_tricount(tricount_id)
    if t is None:
        return jsonify({"error": "Not found"}), 404

    payload = request.get_json() or {}
    name = (payload.get("name") or "").strip()
    email = (payload.get("email") or "").strip() or None

    if not name:
        return jsonify({"error": "Name is required"}), 400

    user = t.add_user(name=name, email=email)
    save_tricounts(tricounts)

    return (
        jsonify({"id": user.id, "name": user.name, "email": user.email}),
        201,
    )


@app.route("/api/tricounts/<tricount_id>/users/<user_id>", methods=["DELETE"])
def api_delete_user(tricount_id: str, user_id: str):
    t = find_tricount(tricount_id)
    if t is None:
        return jsonify({"error": "Not found"}), 404

    for e in t.expenses:
        if e.payer_id == user_id or user_id in e.participants_ids:
            return (
                jsonify(
                    {"error": "Cannot delete this user: used in an expense."}
                ),
                400,
            )

    t.users = [u for u in t.users if u.id != user_id]
    save_tricounts(tricounts)

    return jsonify(tricount_with_balances_to_dict(t)), 200


@app.route("/api/tricounts/<tricount_id>/expenses", methods=["POST"])
def api_add_expense(tricount_id: str):
    t = find_tricount(tricount_id)
    if t is None:
        return jsonify({"error": "Not found"}), 404

    payload = request.get_json() or {}
    description = (payload.get("description") or "").strip()
    amount = payload.get("amount")
    payer_id = payload.get("payer_id")
    participants_ids = payload.get("participants_ids") or []

    if not description:
        return jsonify({"error": "Description is required"}), 400

    try:
        amount = float(amount)
    except Exception:
        return jsonify({"error": "Amount must be number"}), 400

    if not payer_id:
        return jsonify({"error": "Payer is required"}), 400
    if not participants_ids:
        return jsonify({"error": "At least one participant is required"}), 400

    t.add_expense(description, amount, payer_id, participants_ids)
    save_tricounts(tricounts)

    return jsonify(tricount_with_balances_to_dict(t)), 201


@app.route(
    "/api/tricounts/<tricount_id>/expenses/<expense_id>", methods=["DELETE"]
)
def api_delete_expense(tricount_id: str, expense_id: str):
    t = find_tricount(tricount_id)
    if t is None:
        return jsonify({"error": "Not found"}), 404

    t.expenses = [e for e in t.expenses if e.id != expense_id]
    save_tricounts(tricounts)

    return jsonify(tricount_with_balances_to_dict(t)), 200


if __name__ == "__main__":
    app.run(debug=True)
