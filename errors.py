from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from models import (
    ApiaryNotFound,
    AsaliError,
    HarvestRefused,
    HiveNotFound,
)


class InvalidInput(AsaliError):
    def __init__(
        self,
        message: str,
        details: list[dict[str, str]] | None = None,
    ):
        super().__init__(message)
        self.details = details or []


def bad_field(field: str, message: str) -> dict[str, str]:
    return {
        "field": field,
        "message": message,
    }


def register_errors(app: Flask) -> None:
    @app.errorhandler(ApiaryNotFound)
    def handle_apiary_not_found(error: ApiaryNotFound):
        return jsonify({"error": str(error)}), 404

    @app.errorhandler(HiveNotFound)
    def handle_hive_not_found(error: HiveNotFound):
        return jsonify({"error": str(error)}), 404

    @app.errorhandler(HarvestRefused)
    def handle_harvest_refused(error: HarvestRefused):
        return jsonify({"error": str(error)}), 409

    @app.errorhandler(InvalidInput)
    def handle_invalid_input(error: InvalidInput):
        body = {"error": str(error)}

        if error.details:
            body["details"] = error.details

        return jsonify(body), 400

    @app.errorhandler(ValueError)
    def handle_value_error(error: ValueError):
        return jsonify({"error": str(error)}), 400

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        return jsonify({"error": error.description}), error.code