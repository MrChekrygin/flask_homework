from flask import Blueprint, request, jsonify
from app import db
from models import Ad, User

ads_bp = Blueprint("ads", __name__)

@ads_bp.route("/", methods=["POST"])
def create_ad():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    owner_id = data.get("owner_id")

    user = User.query.get(owner_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    ad = Ad(title=title, description=description, owner_id=owner_id)
    db.session.add(ad)
    db.session.commit()

    return jsonify({"message": "Ad created", "id": ad.id}), 201


@ads_bp.route("/<int:ad_id>", methods=["GET"])
def get_ad(ad_id):
    ad = Ad.query.get_or_404(ad_id)
    return jsonify({
        "id": ad.id,
        "title": ad.title,
        "description": ad.description,
        "created_at": ad.created_at,
        "owner": ad.owner.email
    })


@ads_bp.route("/<int:ad_id>", methods=["PUT"])
def update_ad(ad_id):
    ad = Ad.query.get_or_404(ad_id)
    data = request.get_json()

    ad.title = data.get("title", ad.title)
    ad.description = data.get("description", ad.description)
    db.session.commit()

    return jsonify({"message": "Ad updated"})


@ads_bp.route("/<int:ad_id>", methods=["DELETE"])
def delete_ad(ad_id):
    ad = Ad.query.get_or_404(ad_id)
    db.session.delete(ad)
    db.session.commit()
    return jsonify({"message": "Ad deleted"})
