from flask import Blueprint, jsonify

from store import find_hive


bp = Blueprint("hives", __name__, url_prefix="/api/hives")


@bp.get("/<int:hive_id>")
def get_hive(hive_id):
    hive = find_hive(hive_id)
    return jsonify(hive.to_json())