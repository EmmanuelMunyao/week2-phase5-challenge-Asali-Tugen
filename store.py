from datetime import date

from models import (
    Apiary,
    ApiaryNotFound,
    Hive,
    HiveNotFound,
)


APIARIES: dict[str, Apiary] = {}
HIVES: dict[int, Hive] = {}


def add_apiary(apiary: Apiary) -> Apiary:
    APIARIES[apiary.code] = apiary
    return apiary


def add_hive(hive: Hive) -> Hive:
    HIVES[hive.id] = hive
    return hive


def find_apiary(code: str) -> Apiary:
    code = code.upper()

    try:
        return APIARIES[code]
    except KeyError:
        raise ApiaryNotFound(f"No apiary {code}.") from None


def find_hive(hive_id: int) -> Hive:
    try:
        return HIVES[hive_id]
    except KeyError:
        raise HiveNotFound(f"No hive {hive_id}.") from None


def hives_at(code: str) -> list[Hive]:
    apiary = find_apiary(code)
    return [hive for hive in HIVES.values() if hive.apiary is apiary]


# Seed data: three apiaries, six hives, seven harvests
kpr = add_apiary(Apiary("KPR", "Kapropita", "Kiprono Chelimo"))
tng = add_apiary(Apiary("TNG", "Tenges", "Jerotich Kibet"))
mrg = add_apiary(Apiary("MRG", "Marigat", "Rebecca Chepchumba"))

hive = add_hive(Hive(kpr, "top-bar", date(2025, 11, 3)))      # 1
hive.harvest(11.5, date(2026, 3, 14))
hive.harvest(9, date(2026, 7, 18))

hive = add_hive(Hive(kpr, "top-bar", date(2025, 11, 3)))      # 2
hive.harvest(12, date(2026, 3, 14))

hive = add_hive(Hive(kpr, "log", date(2024, 6, 15)))          # 3
hive.harvest(6.5, date(2026, 3, 15))
hive.harvest(7, date(2026, 7, 19))

hive = add_hive(Hive(tng, "langstroth", date(2026, 2, 10)))   # 4
hive.harvest(21.5, date(2026, 7, 25))

hive = add_hive(Hive(tng, "top-bar", date(2026, 2, 10)))      # 5
hive.harvest(13, date(2026, 7, 25))

add_hive(Hive(mrg, "langstroth", date(2026, 7, 1)))           # 6