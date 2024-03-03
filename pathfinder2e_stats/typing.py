from __future__ import annotations

from collections.abc import Iterable
from enum import IntEnum
from itertools import groupby
from typing import TYPE_CHECKING, Any, NamedTuple

if TYPE_CHECKING:
    # TODO import from typing (requires Python >=3.10)
    from typing_extensions import TypeAlias


class DoS(IntEnum):
    critical_failure = -1
    failure = 0
    success = 1
    critical_success = 2


class Damage(NamedTuple):
    type: str
    dice: int
    faces: int
    bonus: int = 0
    multiplier: float = 1
    persistent: bool = False
    splash: bool = False

    def __str__(self) -> str:
        if self.dice and self.faces:
            s = f"{self.dice}d{self.faces}"
            if self.bonus > 0:
                s += f"+{self.bonus}"
            elif self.bonus < 0:
                s += f"-{-self.bonus}"
        else:
            s = str(self.bonus)

        if self.multiplier == 0.5:
            s = f"({s})/2"
        elif self.multiplier != 1:
            s = f"({s})x{self.multiplier}"
        if self.persistent:
            return f"{s} persistent {self.type} damage"
        elif self.splash:
            return f"{s} {self.type} splash damage"
        else:
            return f"{s} {self.type} damage"

    @staticmethod
    def simplify(damages: Iterable[Damage], /) -> list[Damage]:
        # Don't sort e.g. slashing + fire alphabetically
        types_by_appearance: dict[str, int] = {}

        def key(d: Damage) -> tuple:
            return (
                d.splash,  # splash damage last
                d.persistent,  # persistant damage next-to-last
                types_by_appearance.setdefault(d.type, len(types_by_appearance)),
                -d.multiplier,  # Doubled damage first
                -d.faces,  # Largest die size first
            )

        out = []
        for _, group_it in groupby(sorted(damages, key=key), key=key):
            group = list(group_it)
            if len(group) == 1:
                out.append(group[0])
            else:
                out.append(
                    group[0].copy(
                        dice=sum(d.dice for d in group),
                        bonus=sum(d.bonus for d in group),
                    )
                )
            if (
                len(out) > 1
                and out[-1].faces == 0
                and all(
                    getattr(out[-1], k) == getattr(out[-2], k)
                    for k in ("splash", "persistent", "type", "multiplier")
                )
            ):
                # Sum flat bonus to dice
                out[-2:] = [out[-2].copy(bonus=out[-2].bonus + out[-1].bonus)]

        return out

    def copy(self, **kwargs: Any) -> Damage:
        kwargs2 = dict(zip(self.__annotations__, self))
        kwargs2.update(kwargs)
        return Damage(**kwargs2)  # type: ignore[arg-type]


DamageSpec: TypeAlias = dict[DoS, list[Damage]]
