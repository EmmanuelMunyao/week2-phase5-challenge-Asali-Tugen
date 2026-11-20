from datetime import date


def parse_date(value: str, message: str = "Use a date like 2026-09-01.") -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError(message) from None


def require_json(data: object) -> dict:
    if not isinstance(data, dict):
        raise ValueError("The body must be a JSON object.")

    return data