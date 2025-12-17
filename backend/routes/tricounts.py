from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required

from backend.models.currency import Currency
from backend.models.tricount import Tricount
from backend.services.balance import compute_balances
from backend.services.export import export_tricount_to_excel
from backend.services.settlement import compute_settlements
from backend.utils.auth_storage import load_users
from backend.utils.tricount_storage import load_tricounts, save_tricounts

tricount_bp = Blueprint("tricounts", __name__)

tricounts = load_tricounts()


def find_tricount(tricount_id: str) -> Tricount | None:
    """Helper to find a tricount object by ID in our list."""
    return next((t for t in tricounts if t.id == tricount_id), None)


def tricount_with_balances_to_dict(tricount: Tricount) -> dict:
    """Helper to format the full tricount response with calculated balances."""
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
                "weights": e.weights,
            }
            for e in tricount.expenses
        ],
        "balances": balances,
        "settlements": [
            {"from": f, "to": t, "amount": amount}
            for (f, t, amount) in settlements_raw
        ],
    }


@tricount_bp.route("", methods=["GET"])
@jwt_required()
def list_tricounts():
    user_auth_id = get_jwt_identity()
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
            if (
                any(u.auth_id == user_auth_id for u in t.users)
                or t.owner_auth_id == user_auth_id
            )
        ]
    )


@tricount_bp.route("", methods=["POST"])
@jwt_required()
def create_tricount():
    user_auth_id = get_jwt_identity()
    payload = request.get_json() or {}
    name = (payload.get("name") or "").strip()

    if not name:
        return jsonify({"error": "Name is required"}), 400

    t = Tricount(name=name, owner_auth_id=user_auth_id, currency=Currency.EUR)
    tricounts.append(t)
    save_tricounts(tricounts)

    return jsonify(tricount_with_balances_to_dict(t)), 201


@tricount_bp.route("/<tricount_id>", methods=["GET"])
def get_tricount(tricount_id: str):
    t = find_tricount(tricount_id)
    if t is None:
        return jsonify({"error": "Not found"}), 404

    return jsonify(tricount_with_balances_to_dict(t))


@tricount_bp.route("/<tricount_id>/users", methods=["POST"])
def add_user(tricount_id: str):
    t = find_tricount(tricount_id)
    if t is None:
        return jsonify({"error": "Not found"}), 404

    payload = request.get_json() or {}
    name = (payload.get("name") or "").strip()
    email = (payload.get("email") or "").strip() or None

    if not name:
        return jsonify({"error": "Name is required"}), 400

    user = t.add_user(name=name, email=email)
    if email:
        registered_users = load_users()
        matched_account = next(
            (u for u in registered_users if u.email == email), None
        )

        if matched_account:
            user.auth_id = matched_account.id

    save_tricounts(tricounts)

    return (
        jsonify(
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "auth_id": user.auth_id,
            }
        ),
        201,
    )


@tricount_bp.route("/<tricount_id>/users/<user_id>", methods=["DELETE"])
def delete_user(tricount_id: str, user_id: str):
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


@tricount_bp.route("/<tricount_id>/expenses", methods=["POST"])
def add_expense(tricount_id: str):
    t = find_tricount(tricount_id)
    if t is None:
        return jsonify({"error": "Not found"}), 404

    payload = request.get_json() or {}
    description = (payload.get("description") or "").strip()
    amount = payload.get("amount")
    payer_id = payload.get("payer_id")
    participants_ids = payload.get("participants_ids") or []

    weights = payload.get("weights") or {}

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

    t.add_expense(description, amount, payer_id, participants_ids, weights)

    save_tricounts(tricounts)

    return jsonify(tricount_with_balances_to_dict(t)), 201


@tricount_bp.route("/<tricount_id>/expenses/<expense_id>", methods=["DELETE"])
def delete_expense(tricount_id: str, expense_id: str):
    t = find_tricount(tricount_id)
    if t is None:
        return jsonify({"error": "Not found"}), 404

    t.expenses = [e for e in t.expenses if e.id != expense_id]
    save_tricounts(tricounts)

    return jsonify(tricount_with_balances_to_dict(t)), 200


@tricount_bp.route("/<tricount_id>/export/excel", methods=["GET"])
def export_tricount_excel(tricount_id: str):
    tricount = find_tricount(tricount_id)
    if tricount is None:
        return jsonify({"error": "Not found"}), 404

    output = export_tricount_to_excel(tricount)
    filename = (
        f"tricount_{(tricount.name or tricount.id).replace(' ', '_')}.xlsx"
    )

    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@tricount_bp.route("/<tricount_id>", methods=["DELETE"])
def delete_tricount(tricount_id: str):

    tricount = find_tricount(tricount_id)
    if tricount is None:
        return jsonify({"error": "Tricount introuvable"}), 404

    tricounts[:] = [t for t in tricounts if t.id != tricount_id]

    save_tricounts(tricounts)

    return "", 204
