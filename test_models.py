
from datetime import date

import pytest

from models import (
    Apiary,
    HarvestRefused,
    Hive,
    KINDS,
)


SITE = Apiary("TST", "Test site", "Test host")


def new_hive(
    kind: str = "top-bar",
    installed_on: date = date(2026, 1, 5),
) -> Hive:
    return Hive(SITE, kind, installed_on)


def test_next_harvest_is_60_days_later():
    hive = new_hive()

    hive.harvest(9, date(2026, 3, 1))

    assert hive.total_kg() == 9.0
    assert hive.next_harvest_from() == date(2026, 4, 30)


def test_harvest_is_stored_as_float():
    hive = new_hive()

    harvest = hive.harvest(8, date(2026, 3, 1))

    assert harvest.kg == 8.0
    assert isinstance(harvest.kg, float)


def test_harvest_to_json():
    hive = new_hive()

    harvest = hive.harvest(9.5, date(2026, 3, 1))

    assert harvest.to_json() == {
        "kg": 9.5,
        "harvested_on": "2026-03-01",
    }


def test_total_kg_is_rounded_to_one_decimal():
    hive = new_hive()

    hive.harvest(8.4, date(2026, 3, 1))
    hive.harvest(9.1, date(2026, 4, 30))

    assert hive.total_kg() == 17.5


def test_last_harvest_returns_latest_date():
    hive = new_hive()

    hive.harvest(8, date(2026, 3, 1))
    hive.harvest(7, date(2026, 4, 30))

    assert hive.last_harvest() == date(2026, 4, 30)


def test_no_harvest_has_no_last_or_next_date():
    hive = new_hive()

    assert hive.last_harvest() is None
    assert hive.next_harvest_from() is None


@pytest.mark.parametrize(
    ("kind", "maximum"),
    [
        ("top-bar", 15.0),
        ("langstroth", 25.0),
        ("log", 10.0),
    ],
)
def test_hive_kinds_have_correct_limits(kind: str, maximum: float):
    assert KINDS[kind] == maximum


@pytest.mark.parametrize(
    ("kind", "weight", "message"),
    [
        (
            "top-bar",
            16,
            "A top-bar hive gives at most 15 kg in one harvest.",
        ),
        (
            "langstroth",
            26,
            "A langstroth hive gives at most 25 kg in one harvest.",
        ),
        (
            "log",
            11,
            "A log hive gives at most 10 kg in one harvest.",
        ),
    ],
)
def test_weight_cannot_exceed_hive_limit(
    kind: str,
    weight: float,
    message: str,
):
    hive = new_hive(kind)

    with pytest.raises(ValueError, match=message):
        hive.harvest(weight, date(2026, 3, 1))


def test_weight_must_be_above_zero():
    hive = new_hive()

    with pytest.raises(ValueError, match="Use a weight above 0 kg."):
        hive.harvest(0, date(2026, 3, 1))


def test_negative_weight_is_refused():
    hive = new_hive()

    with pytest.raises(ValueError, match="Use a weight above 0 kg."):
        hive.harvest(-2, date(2026, 3, 1))


def test_hive_cannot_be_harvested_before_installation():
    hive = new_hive(installed_on=date(2026, 5, 1))

    with pytest.raises(
        ValueError,
        match="Hive .* was installed on 2026-05-01.",
    ):
        hive.harvest(5, date(2026, 4, 30))


def test_harvest_too_soon_is_refused():
    hive = new_hive()

    hive.harvest(9, date(2026, 3, 1))

    with pytest.raises(
        HarvestRefused,
        match=(
            "Hive .* was last harvested on 2026-03-01; "
            "harvest again from 2026-04-30."
        ),
    ):
        hive.harvest(5, date(2026, 4, 29))


def test_harvest_on_exact_next_day_is_allowed():
    hive = new_hive()

    hive.harvest(9, date(2026, 3, 1))
    second = hive.harvest(5, date(2026, 4, 30))

    assert second.kg == 5.0
    assert hive.total_kg() == 14.0


def test_refused_harvest_does_not_change_history():
    hive = new_hive()

    hive.harvest(9, date(2026, 3, 1))

    with pytest.raises(HarvestRefused):
        hive.harvest(5, date(2026, 4, 29))

    assert len(hive.harvests) == 1
    assert hive.total_kg() == 9.0


def test_unknown_hive_kind_is_rejected():
    with pytest.raises(ValueError, match="Unknown hive kind: box"):
        new_hive("box")
