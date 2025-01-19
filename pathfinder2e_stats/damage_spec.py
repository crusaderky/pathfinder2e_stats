from __future__ import annotations

import warnings
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
    fatal_aim: int = 0
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
        for faces in (
            self.faces,
            self.two_hands,
            self.deadly,
            self.fatal,
            self.fatal_aim,
        ):
            if faces not in {0, 2, 4, 6, 8, 10, 12}:
                raise ValueError(f"Invalid dice faces: {faces}")
        if (self.dice == 0) != (self.faces == 0):
            raise ValueError(
                f"dice and faces must be both zero or both non-zero; got {self}"
            )
        if self.multiplier not in (0.5, 1, 2):
            raise ValueError(f"multiplier must be 0.5, 1, or 2; got {self.multiplier}")
        if self.persistent and self.splash:
            raise ValueError("Damage can't be both persistent and splash")
        if self.fatal and self.fatal_aim:
            raise ValueError("Can't have both fatal and fatal aim traits")

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
        if self.fatal_aim:
            s += f" fatal aim d{self.fatal_aim}"

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
                d.persistent,  # persistent damage next-to-last
                types_by_appearance.setdefault(d.type, len(types_by_appearance)),
                -d.multiplier,  # Doubled damage first
                -d.faces,  # Largest die size first
                d.two_hands,
                d.deadly,
                d.fatal,
                d.fatal_aim,
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
        kwargs2 = {k: getattr(self, k) for k in self.__annotations__}
        kwargs2.update(kwargs)
        return Damage(**kwargs2)

    def hands(self, hands: Literal[1, 2]) -> Damage:
        if hands not in (1, 2) or hands is True:
            raise ValueError("Must use 1 or 2 hands to wield")
        if self.two_hands:
            return self.copy(
                faces=self.two_hands if hands == 2 else self.faces, two_hands=0
            )
        if self.fatal_aim:
            return self.copy(fatal=self.fatal_aim if hands == 2 else 0, fatal_aim=0)
        raise ValueError("Weapon does not have the two-hands or fatal aim traits")

    def _auto_two_hands(self) -> Damage:
        if self.two_hands or self.fatal_aim:
            warnings.warn(
                "Assuming weapon is held in two hands. "
                "You should explicitly call .hands(2) or .hands(1).",
                stacklevel=2,
            )
            return self.hands(2)
        return self

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
        return self.copy(dice=self.dice + dice)

    def expand(self) -> ExpandedDamage:
        self = self._auto_two_hands()  # noqa: PLW0642
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
            if self.dice == 0 and self.bonus > 0:
                # Minimum 1 damage on a save
                out[DoS.success] = [base.copy(bonus=max(1, self.bonus // 2))]
            elif self.dice > 0:
                out[DoS.success] = [base.copy(multiplier=0.5)]

        return ExpandedDamage(out)

    def __add__(self, other: AnyDamageSpec) -> DamageList | ExpandedDamage:
        """Add two damage specs together"""
        d = self._auto_two_hands()
        return DamageList([d]) + other


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

    def filter(
        self, *which: Literal["direct", "persistent", "splash"]
    ) -> ExpandedDamage:
        which_set = set(which)
        if unknown := which_set - {"direct", "persistent", "splash"}:
            raise ValueError(f"Unknown filter(s): {list(unknown)}")

        select_direct = "direct" in which_set
        select_persistent = "persistent" in which_set
        select_splash = "splash" in which_set

        def match(d: Damage) -> bool:
            if d.persistent:
                return select_persistent
            if d.splash:
                return select_splash
            return select_direct

        return ExpandedDamage({k: [d for d in v if match(d)] for k, v in self.items()})

    def to_dict_of_str(self) -> dict[str, str]:
        return {str(k): str(DamageList(v)) for k, v in self.items()}


AnyDamageSpec: TypeAlias = (
    Damage
    | Iterable[Damage]
    | ExpandedDamage
    | Mapping[int, Collection[Damage]]
    | Mapping[DoS, Collection[Damage]]
)
