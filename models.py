from dataclasses import dataclass
from datetime import date, timedelta
from typing import ClassVar


KINDS = {
    "top-bar": 15.0,
    "langstroth": 25.0,
    "log": 10.0,
}

HARVEST_WAIT_DAYS = 60


class AsaliError(Exception):
    """Base error for Asali Tugen business rules."""


class ApiaryNotFound(AsaliError, LookupError):
    """Raised when an apiary cannot be found."""


class HiveNotFound(AsaliError, LookupError):
    """Raised when a hive cannot be found."""


class HarvestRefused(AsaliError):
    """Raised when a harvest violates the waiting-period rule."""


@dataclass(frozen=True)
class Apiary:
    code: str
    name: str
    host: str


@dataclass(frozen=True)
class Harvest:
    kg: float
    harvested_on: date

    def to_json(self) -> dict[str, object]:
        return {
            "kg": self.kg,
            "harvested_on": self.harvested_on.isoformat(),
        }


class Hive:
    next_id: ClassVar[int] = 1

    def __init__(
        self,
        apiary: Apiary,
        kind: str,
        installed_on: date,
    ) -> None:
        if kind not in KINDS:
            raise ValueError(f"Unknown hive kind: {kind}")

        self.id = Hive.next_id
        Hive.next_id += 1

        self.apiary = apiary
        self.kind = kind
        self.installed_on = installed_on
        self.harvests: list[Harvest] = []

    def total_kg(self) -> float:
        return round(sum(harvest.kg for harvest in self.harvests), 1)

    def last_harvest(self) -> date | None:
        if not self.harvests:
            return None

        return max(harvest.harvested_on for harvest in self.harvests)

    def next_harvest_from(self) -> date | None:
        last = self.last_harvest()

        if last is None:
            return None

        return last + timedelta(days=HARVEST_WAIT_DAYS)

    def harvest(self, kg: float, on: date) -> Harvest:
        if kg <= 0:
            raise ValueError("Use a weight above 0 kg.")

        maximum = KINDS[self.kind]

        if kg > maximum:
            raise ValueError(
                f"A {self.kind} hive gives at most {maximum:g} kg in one harvest."
            )

        if on < self.installed_on:
            raise ValueError(
                f"Hive {self.id} was installed on "
                f"{self.installed_on.isoformat()}."
            )

        next_harvest = self.next_harvest_from()

        if next_harvest is not None and on < next_harvest:
            last = self.last_harvest()

            raise HarvestRefused(
                f"Hive {self.id} was last harvested on "
                f"{last.isoformat()}; harvest again from "
                f"{next_harvest.isoformat()}."
            )

        new_harvest = Harvest(float(kg), on)
        self.harvests.append(new_harvest)

        return new_harvest

    def to_json(self) -> dict[str, object]:
        return {
            "apiary": self.apiary.code,
            "harvests": len(self.harvests),
            "id": self.id,
            "installed_on": self.installed_on.isoformat(),
            "kind": self.kind,
            "last_harvest": (
                self.last_harvest().isoformat()
                if self.last_harvest() is not None
                else None
            ),
            "next_harvest_from": (
                self.next_harvest_from().isoformat()
                if self.next_harvest_from() is not None
                else None
            ),
            "total_kg": self.total_kg(),
        }

    def __repr__(self) -> str:
        return (
            f"Hive(id={self.id}, apiary={self.apiary.code!r}, "
            f"kind={self.kind!r}, installed_on={self.installed_on!r})"
        )