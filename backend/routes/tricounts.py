from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required

from backend.models.currency import Currency
from backend.models.tricount import Tricount
from backend.services.export import export_tricount_to_excel
from backend.utils.tricount_storage import load_tricounts, save_tricounts
from backend.utils.utils import (
    get_tricount_from_id,
    get_tricount_from_id_with_permissions,
    tricount_with_balances_to_dict,
)

tricount_bp = Blueprint("tricounts", __name__)

tricounts = load_tricounts()


@tricount_bp.route("", methods=["GET"])
@jwt_required()
def list_tricounts():
    user_email = get_jwt_identity()
    return jsonify(
        [
            {
                "id": tricount.id,
                "name": tricount.name,
                "currency": tricount.currency.value,
                "users_count": len(tricount.users),
                "expenses_count": len(tricount.expenses),
            }
            for tricount in tricounts
            if (
                any(u.email == user_email for u in tricount.users)
                or tricount.owner_email == user_email
            )
        ]
    )


@tricount_bp.route("", methods=["POST"])
@jwt_required()
def create_tricount():
    user_email = get_jwt_identity()
    payload = request.get_json() or {}
    name = (payload.get("name") or "").strip()

    if not name:
        return jsonify({"error": "Un nom est requis"}), 400

    tricount = Tricount(
        name=name, owner_email=user_email, currency=Currency.EUR
    )
    tricounts.append(tricount)
    save_tricounts(tricounts=tricounts)

    return jsonify(tricount_with_balances_to_dict(tricount=tricount)), 201


@tricount_bp.route("/<tricount_id>", methods=["GET"])
@jwt_required()
def get_tricount(tricount_id: str):
    tricount = get_tricount_from_id_with_permissions(
        tricount_id, tricounts=tricounts, user_email=get_jwt_identity()
    )
    return jsonify(tricount_with_balances_to_dict(tricount=tricount))


@tricount_bp.route("/<tricount_id>/users", methods=["POST"])
@jwt_required()
def add_user(tricount_id: str):
    tricount = get_tricount_from_id_with_permissions(
        tricount_id=tricount_id,
        tricounts=tricounts,
        user_email=get_jwt_identity(),
    )
    user_email = get_jwt_identity()

    payload = request.get_json() or {}
    name = (payload.get("name") or "").strip()
    email = (payload.get("email") or "").strip() or user_email

    if not name:
        return jsonify({"error": "Un nom est requis"}), 400

    if any(u.name == name for u in tricount.users):
        return (
            jsonify(
                {"error": "Ce nom est déjà utilisé par un autre utilisateur"}
            ),
            409,
        )

    user = tricount.add_user(name=name, email=email)

    save_tricounts(tricounts=tricounts)

    return (
        jsonify(
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
            }
        ),
        201,
    )


@tricount_bp.route("/<tricount_id>/users/<user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(tricount_id: str, user_id: str):
    tricount = get_tricount_from_id_with_permissions(
        tricount_id=tricount_id,
        tricounts=tricounts,
        user_email=get_jwt_identity(),
        owner_needed=True,
    )

    for e in tricount.expenses:
        if e.payer_id == user_id or user_id in e.participants_ids:
            return (
                jsonify(
                    {
                        "error": "Impossible de supprimer cet utilisateur : utilisé dans une dépense."
                    }
                ),
                400,
            )

    tricount.users = [u for u in tricount.users if u.id != user_id]
    save_tricounts(tricounts=tricounts)

    return jsonify(tricount_with_balances_to_dict(tricount=tricount)), 200


@tricount_bp.route("/<tricount_id>/expenses", methods=["POST"])
@jwt_required()
def add_expense(tricount_id: str):
    tricount = get_tricount_from_id_with_permissions(
        tricount_id=tricount_id,
        tricounts=tricounts,
        user_email=get_jwt_identity(),
    )

    payload = request.get_json() or {}
    description = (payload.get("description") or "").strip()
    amount = payload.get("amount")
    payer_id = payload.get("payer_id")
    participants_ids = payload.get("participants_ids") or []

    weights = payload.get("weights") or {}

    if not description:
        return jsonify({"error": "La description est requise"}), 400

    try:
        amount = float(amount)
    except Exception:
        return jsonify({"error": "Le montant doit être un nombre"}), 400

    if not payer_id:
        return jsonify({"error": "Le payeur est requis"}), 400
    if not participants_ids:
        return jsonify({"error": "Au moins un participant est requis"}), 400

    tricount.add_expense(
        description=description,
        amount=amount,
        payer_id=payer_id,
        participants_ids=participants_ids,
        weights=weights,
    )

    save_tricounts(tricounts=tricounts)

    return jsonify(tricount_with_balances_to_dict(tricount=tricount)), 201


@tricount_bp.route("/<tricount_id>/expenses/<expense_id>", methods=["DELETE"])
@jwt_required()
def delete_expense(tricount_id: str, expense_id: str):
    tricount = get_tricount_from_id_with_permissions(
        tricount_id=tricount_id,
        tricounts=tricounts,
        user_email=get_jwt_identity(),
    )

    tricount.expenses = [e for e in tricount.expenses if e.id != expense_id]
    save_tricounts(tricounts=tricounts)

    return jsonify(tricount_with_balances_to_dict(tricount=tricount)), 200


@tricount_bp.route("/<tricount_id>/export/excel", methods=["GET"])
@jwt_required()
def export_tricount_excel(tricount_id: str):
    tricount = get_tricount_from_id_with_permissions(
        tricount_id=tricount_id,
        tricounts=tricounts,
        user_email=get_jwt_identity(),
    )

    output = export_tricount_to_excel(tricount=tricount)
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
@jwt_required()
def delete_tricount(tricount_id: str):
    tricount = get_tricount_from_id_with_permissions(
        tricount_id=tricount_id,
        tricounts=tricounts,
        user_email=get_jwt_identity(),
        owner_needed=True,
    )

    tricounts[:] = [t for t in tricounts if t.id != tricount_id]
    save_tricounts(tricounts=tricounts)
    return "", 204


@tricount_bp.route("/<tricount_id>/invite", methods=["GET"])
@jwt_required()
def invite_new_user(tricount_id: str):
    tricount = get_tricount_from_id_with_permissions(
        tricount_id=tricount_id,
        tricounts=tricounts,
        user_email=get_jwt_identity(),
    )
    return jsonify({"tricount_id": tricount.id})


@tricount_bp.route("/<tricount_id>/users", methods=["GET"])
@jwt_required()
def get_users(tricount_id: str):
    tricount = get_tricount_from_id(
        tricount_id=tricount_id, tricounts=tricounts
    )
    return (
        jsonify(
            [
                {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                }
                for user in tricount.users
            ]
        ),
        200,
    )


@tricount_bp.route("/<tricount_id>/join", methods=["POST"])
@jwt_required()
def join_tricount(tricount_id: str):
    user_email = get_jwt_identity()
    tricount = get_tricount_from_id(
        tricount_id=tricount_id, tricounts=tricounts
    )

    payload = request.get_json() or {}
    name = (payload.get("name") or "").strip()
    user_id = payload.get("user_id")
    email = (payload.get("email") or "").strip() or user_email

    if not user_id:
        user = tricount.add_user(name=name, email=email)
    else:
        if not name:
            return jsonify({"error": "Un nom est requis"}), 400
        user = tricount.modify_user_email(user_id=user_id, email=user_email)

    save_tricounts(tricounts=tricounts)

    return (
        jsonify(
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
            }
        ),
        201,
    )
