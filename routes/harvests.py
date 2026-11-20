from flask import Blueprint, jsonify, request

from inputs import parse_date, require_json
from store import HIVES, find_hive


bp = Blueprint("harvests", __name__, url_prefix="/api")


@bp.get("/harvests")
def all_harvests():
    apiary = request.args.get("apiary")
    from_date = request.args.get("from")
    to_date = request.args.get("to")

    start = parse_date(from_date) if from_date else None
    end = parse_date(to_date) if to_date else None

    results = []

    for hive in HIVES.values():
        if apiary and hive.apiary.code != apiary:
            continue

        for harvest in hive.harvests:
            if start and harvest.harvested_on < start:
                continue

            if end and harvest.harvested_on > end:
                continue

            results.append(harvest.to_json())

    return jsonify(results)


@bp.get("/hives/<int:hive_id>/harvests")
def list_harvests(hive_id):
    hive = find_hive(hive_id)

    return jsonify([
        harvest.to_json()
        for harvest in hive.harvests
    ])


@bp.post("/hives/<int:hive_id>/harvests")
def create_harvest(hive_id):
    hive = find_hive(hive_id)
    data = require_json(request.get_json(silent=True))

    if "kg" not in data or "harvested_on" not in data:
        raise ValueError("kg and harvested_on are required.")

    harvest = hive.harvest(
        float(data["kg"]),
        parse_date(str(data["harvested_on"])),
    )

    return jsonify(harvest.to_json()), 201