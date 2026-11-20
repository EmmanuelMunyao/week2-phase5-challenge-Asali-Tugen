from flask import Blueprint, jsonify, current_app


bp = Blueprint("home", __name__)


@bp.get("/")
def home():
    price = current_app.config["HONEY_PRICE_KSH"]

    return (
        f"Asali Tugen honey API. "
        f"Raw honey KSh {price:,} a kg. "
        f"Try /api/health or /api/apiaries."
    )


@bp.get("/api/health")
def health():
    return jsonify({"status": "ok"})