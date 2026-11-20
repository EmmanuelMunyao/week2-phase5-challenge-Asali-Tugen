from flask import Blueprint, abort, jsonify, request

from errors import InvalidInput, bad_field
from models import Apiary
from store import APIARIES, add_apiary, find_apiary, hives_at


bp = Blueprint("apiaries", __name__, url_prefix="/api/apiaries")


def apiary_to_json(apiary: Apiary) -> dict:
    hives = hives_at(apiary.code)

    return {
        "code": apiary.code,
        "hives": len(hives),
        "host": apiary.host,
        "name": apiary.name,
        "total_kg": round(sum(hive.total_kg() for hive in hives), 1),
    }


@bp.get("")
def list_apiaries():
    return jsonify(
        [apiary_to_json(apiary) for apiary in APIARIES.values()]
    )


@bp.get("/<code>")
def get_apiary(code: str):
    apiary = find_apiary(code)
    return jsonify(apiary_to_json(apiary))


@bp.post("")
def create_apiary():
    if not request.is_json:
        abort(
            415,
            description="Send JSON with Content-Type: application/json.",
        )

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        raise InvalidInput("The body must be a JSON object.")

    details = []

    code = data.get("code")
    name = data.get("name")
    host = data.get("host")

    if not isinstance(code, str) or len(code) != 3 or not code.isalpha():
        details.append(
            bad_field("code", "Use 3 letters, like KBT.")
        )

    if not isinstance(name, str) or not name.strip():
        details.append(
            bad_field("name", "Required.")
        )

    if not isinstance(host, str) or not host.strip():
        details.append(
            bad_field("host", "Required.")
        )

    if details:
        raise InvalidInput("Invalid apiary.", details)

    code = code.upper()

    if code in APIARIES:
        abort(
            409,
            description=f"Apiary {code} already exists.",
        )

    apiary = add_apiary(
        Apiary(
            code,
            name.strip(),
            host.strip(),
        )
    )

    response = jsonify(apiary_to_json(apiary))
    response.status_code = 201
    response.headers["Location"] = f"/api/apiaries/{apiary.code}"

    return response