from __future__ import annotations

from collections import UserDict, UserList
from collections.abc import Collection, Iterable, Mapping
from dataclasses import dataclass
from itertools import groupby
from typing import Any, Literal, TypeAlias

from pathfinder2e_stats.check import DoS


@dataclass(frozen=True, slots=True)
class Damage:
    type: str
    dice: int
    faces: int
    bonus: int = 0
    multiplier: float = 1
    persistent: bool = False
    splash: bool = False
    two_hands: int = 0
    deadly: int = 0
    fatal: int = 0
    basic_save: bool = False

    def __post_init__(self) -> None:
        for k, t in self.__annotations__.items():
            cls = eval(t)
            v = getattr(self, k)
            if cls is float:
                if type(v) not in (int, float):
                    raise TypeError(f"{k} must be of type int or float; got {type(v)}")
            elif type(v) is not cls:
                raise TypeError(f"{k} must be of type {t}; got {type(v)}")
        if self.dice < 0:
            raise ValueError(f"dice must be non-negative; got {self.dice}")
        if self.faces not in (0, 2, 4, 6, 8, 10, 12):
            raise ValueError(f"Invalid faces: {self.faces}")
        if (self.dice == 0) != (self.faces == 0):
            raise ValueError(
                f"dice and faces must be both zero or both non-zero; got {self}"
            )
        if self.multiplier not in (0.5, 1, 2):
            raise ValueError(f"multiplier must be 0.5, 1, or 2; got {self.multiplier}")
        if self.persistent and self.splash:
            raise ValueError("Damage can't be both persistent and splash")

    def __repr__(self) -> str:
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
            s += f" persistent {self.type}"
        elif self.splash:
            s += f" {self.type} splash"
        else:
            s += f" {self.type}"

        if self.two_hands:
            s += f" two-hands d{self.two_hands}"
        if self.deadly:
            s += f" deadly d{self.deadly}"
        if self.fatal:
            s += f" fatal d{self.fatal}"

        if self.basic_save:
            s += ", with a basic saving throw"
        return s

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
                d.two_hands,
                d.deadly,
                d.fatal,
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

        return [o for o in out if bool(o)]

    def copy(self, **kwargs: Any) -> Damage:
        kwargs2 = {k: getattr(self, k) for k in self.__annotations__}
        kwargs2.update(kwargs)
        return Damage(**kwargs2)

    def hands(self, n_hands: Literal[1, 2]) -> Damage:
        if not self.two_hands:
            raise ValueError("Weapon does not have the two-hands trait")
        elif n_hands == 1 and n_hands is not True:
            return self.copy(two_hands=0)
        elif n_hands == 2:
            return self.copy(faces=self.two_hands, two_hands=0)
        else:
            raise ValueError("Must use 1 or 2 hands to wield")

    def reduce_die(self) -> Damage:
        return self.copy(faces=self.faces - 2)

    def increase_die(self) -> Damage:
        return self.copy(faces=self.faces + 2)

    def vicious_swing(self, dice: int = 1) -> AnyDamageSpec:
        """Vicious Swing / Power Attack and similar effects

        Add extra weapon dice, which impact the fatal trait but
        not the deadly trait
        """
        if self.deadly:
            return self.expand() + {
                DoS.critical_success: [
                    Damage(self.type, dice, self.fatal or self.faces, multiplier=2)
                ],
                DoS.success: [Damage(self.type, dice, self.faces)],
            }
        else:
            return self.copy(dice=self.dice + dice)

    def _check_two_hands(self) -> None:
        if self.two_hands:
            raise ValueError(
                "Weapon has the two-hands trait; please call "
                ".hands(1) or .hands(2) method"
            )

    def expand(self) -> ExpandedDamage:
        self._check_two_hands()

        base = self.copy(deadly=0, fatal=0, multiplier=1, basic_save=False)
        out = {}

        if self.splash:
            out[DoS.failure] = [base]
        out[DoS.success] = [base]
        if self.fatal:
            out[DoS.critical_success] = [
                base.copy(faces=self.fatal, multiplier=2),
                base.copy(dice=1, faces=self.fatal, bonus=0),
            ]
        else:
            if self.splash:
                crit = base
            elif self.dice == 0:
                crit = base.copy(bonus=base.bonus * 2)
            else:
                crit = base.copy(multiplier=2)
            out[DoS.critical_success] = [crit]
        if self.deadly:
            out[DoS.critical_success].append(
                base.copy(dice=max(1, self.dice - 1), faces=self.deadly, bonus=0)
            )

        if self.basic_save:
            out[DoS.critical_failure] = out.pop(DoS.critical_success)
            out[DoS.failure] = out.pop(DoS.success)
            if self.dice == 0 and self.bonus > 1:
                out[DoS.success] = [base.copy(bonus=self.bonus // 2)]
            elif self.dice > 0:
                out[DoS.success] = [base.copy(multiplier=0.5)]

        return ExpandedDamage(out)

    def __add__(self, other: AnyDamageSpec) -> DamageList | ExpandedDamage:
        """Add two damage specs together"""
        self._check_two_hands()
        return DamageList([self]) + other

    def __bool__(self) -> bool:
        """Return True if rolled damage can be more than zero; False otherwise."""
        return self.dice * (self.fatal or self.faces) + self.bonus + self.deadly > 0


class DamageList(UserList[Damage]):
    @property
    def basic_save(self) -> bool:
        return self[0].basic_save

    def __repr__(self) -> str:
        return " plus ".join(str(el) for el in self)

    def expand(self) -> ExpandedDamage:
        return ExpandedDamage.sum(self)

    def simplify(self) -> DamageList:
        return DamageList(Damage.simplify(self))

    def __add__(self, other: AnyDamageSpec) -> DamageList | ExpandedDamage:  # type: ignore[override]
        if isinstance(other, Damage):
            other = [other]
        if not isinstance(other, Mapping):
            return DamageList([*self, *other]).simplify()
        return self.expand() + other

    __iadd__ = __add__  # type: ignore[assignment]


class ExpandedDamage(UserDict[DoS, list[Damage]]):
    def __init__(
        self,
        data: AnyDamageSpec | None = None,
        /,
    ):
        if data is None:
            data = {}
        elif isinstance(data, Damage):
            data = data.expand().data
        elif not isinstance(data, Mapping):
            data = ExpandedDamage.sum(data).data
        else:
            data = {DoS(k): list(v) for k, v in data.items()}

        data = {k: [vi for vi in v if bool(vi)] for k, v in data.items()}
        data = {k: v for k, v in data.items() if v}
        self.data = dict(sorted(data.items(), reverse=True))  # success > failure

    def __add__(self, other: AnyDamageSpec) -> ExpandedDamage:
        return ExpandedDamage.sum([self, other])

    @staticmethod
    def sum(items: Iterable[AnyDamageSpec]) -> ExpandedDamage:
        out: dict[DoS, list[Damage]] = {}
        for item in items:
            item = ExpandedDamage(item)
            for k, v in item.items():
                out.setdefault(k, []).extend(v)

        out = {k: Damage.simplify(v) for k, v in out.items()}
        return ExpandedDamage(out)

    def _repr_html_(self) -> str:
        out = []
        for k, v in self.items():
            name = k.name.replace("_", " ").capitalize()
            out.append(f"<b>{name}:</b> {DamageList(v)}")
        return "<br>\n".join(out)

    def __repr__(self) -> str:
        return (
            self._repr_html_()
            .replace("<b>", "**")
            .replace("</b>", "**")
            .replace("<br>", "")
        )

    def filter(self, persistent: bool = False, splash: bool = False) -> ExpandedDamage:
        return ExpandedDamage(
            {
                k: [d for d in v if d.persistent is persistent and d.splash is splash]
                for k, v in self.items()
            }
        )

    def to_dict_of_str(self) -> dict[str, str]:
        return {str(k): str(DamageList(v)) for k, v in self.items()}


AnyDamageSpec: TypeAlias = (
    Damage
    | Iterable[Damage]
    | ExpandedDamage
    | Mapping[int, Collection[Damage]]
    | Mapping[DoS, Collection[Damage]]
)
