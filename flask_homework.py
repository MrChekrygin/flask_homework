from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ads.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "key" 

db = SQLAlchemy(app)
jwt = JWTManager(app)

# МОДЕЛИ

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class Advertisement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


# РЕГИСТРАЦИЯ И ЛОГИН

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Email and password required"}), 400

    # Проверяем, что email уникален
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "User already exists"}), 400

    hashed_password = generate_password_hash(data["password"])
    new_user = User(email=data["email"], password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=data["email"]).first()
    if not user or not check_password_hash(user.password_hash, data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=user.id)
    return jsonify({"access_token": token})


# ОБЪЯВЛЕНИЯ

@app.route("/ads", methods=["POST"])
@jwt_required()
def create_ad():
    data = request.get_json()
    user_id = get_jwt_identity()
    new_ad = Advertisement(
        title=data["title"],
        description=data["description"],
        owner_id=user_id
    )
    db.session.add(new_ad)
    db.session.commit()
    return jsonify({"message": "Ad created", "id": new_ad.id}), 201


@app.route("/ads/<int:ad_id>", methods=["GET"])
def get_ad(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)
    return jsonify({
        "id": ad.id,
        "title": ad.title,
        "description": ad.description,
        "created_at": ad.created_at,
        "owner_id": ad.owner_id
    })


@app.route("/ads/<int:ad_id>", methods=["PUT"])
@jwt_required()
def update_ad(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)
    user_id = get_jwt_identity()

    if ad.owner_id != user_id:
        return jsonify({"error": "You can edit only your ads"}), 403

    data = request.get_json()
    if "title" in data:
        ad.title = data["title"]
    if "description" in data:
        ad.description = data["description"]

    db.session.commit()
    return jsonify({"message": "Ad updated"})


@app.route("/ads/<int:ad_id>", methods=["DELETE"])
@jwt_required()
def delete_ad(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)
    user_id = get_jwt_identity()

    if ad.owner_id != user_id:
        return jsonify({"error": "You can delete only your ads"}), 403

    db.session.delete(ad)
    db.session.commit()
    return jsonify({"message": "Ad deleted"})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
