from __future__ import annotations

import warnings
from collections import UserDict, UserList
from collections.abc import Collection, Iterable, Mapping
from dataclasses import dataclass
from itertools import groupby
from typing import Any, Literal, TypeAlias, overload

from pathfinder2e_stats.check import DoS


@dataclass(frozen=True, slots=True)
class Damage:
    """Damage roll specification, e.g. for a weapon or a spell.

    :param str type:
        Damage type, e.g. "fire".
    :param int dice:
        Number of dice to roll.
    :param int faces:
        Number of faces on each die.
    :param int bonus:
        Flat bonus to add to the roll.
    :param bool persistent:
        Whether the damage is persistent.
        It is tracked separately by :func:`damage`. Default: False.
    :param bool splash:
        Whether the damage is splash.
        Splash damage is applied on a simple miss and doesn't
        double on a critical hit. It is tracked separately by
        :func:`damage`. Default: False.

    The following parameters can only be used when using :class:`Damage` on its own,
    and never while manually building an :class:`ExpandedDamage`:

    :param int two_hands:
        Number of faces on the die when using a weapon with the ``two-hands dX`` trait
        in two hands. Before expanding the damage, you will need to call the
        :meth:`hands` method to clarify how many hands you're using.
        Default: no `two-hands` trait.
    :param int deadly:
        Number of faces on the extra dice to add on a critical hit for weapons
        with the ``deadly dX`` trait. Default: no `deadly` trait.
    :param int fatal:
        Number of faces to promote all dice to and for the extra die on critical hits
        with a weapon with the ``fatal dX`` trait. Default: no ``fatal`` trait.
    :param int fatal_aim:
        Number of faces to promote all dice to and for the extra die on critical hits
        with a weapon with the ``fatal aim dX`` trait that is being held in two hands.
        Before expanding the damage, you will need to call the :meth:`hands`
        method to clarify how many hands you're using.
        Default: no `fatal aim` trait.
    :param bool basic_save:
        False (default)
            This is a weapon or an attack spell that follows the normal rules for
            Strikes and spell attack rolls: full damage on a success,
            double damage on a critical success, and no damage on a failure.

            This can be altered by the `splash` trait.
        True
            This is a spell with a basic saving throw: full damage on a failure,
            double damage on a critical failure, half damage on a success
            and no damage on a critical success.

    The following parameter can only be used when manually building a
    :class:`ExpandedDamage`:

    :param float multiplier:
        0.5, 1, or 2. Number to multiply the damage by after rolling it.

    **Compact damage specification**

    Basic weapons and most spells can be specified with a single :class:`Damage`.
    e.g. a :prd_spells:`Fireball <1530>`:

    >>> Damage("fire", 6, 6, basic_save=True)
    **Damage** 6d6 fire, with a basic saving throw

    A *+1 striking longbow*:

    >>> Damage("piercing", 2, 8, deadly=10)
    **Damage** 2d8 piercing deadly d10

    You can define effects such as weapons with runes by chaining :class:`Damage`
    instances with the ``+`` operator. For example:

    A *+1 striking wounding longsword*, wielded by a PC with a +4 STR modifier:

    >>> Damage("slashing", 2, 8, 4) + Damage("bleed", 1, 6, persistent=True)
    **Damage** 2d8+4 slashing plus 1d6 persistent bleed

    A weapon or spell with direct, splash and/or persistent component can be specified
    by adding everything up with ``+``. For example, an
    :prd_equipment:`Alchemist's Fire <3287>`:

    >>> (Damage("fire", 1, 8)
    ... + Damage("fire", 0, 0, 1, persistent=True)
    ... + Damage("fire", 0, 0, 1, splash=True))
    **Damage** 1d8 fire plus 1 persistent fire plus 1 fire splash

    **Complex cases**

    Some damage profiles follow neither the general rule for weapons and attack spells
    nor the rule for basic saving throws. To define them, you need to use
    :class:`ExpandedDamage` instead.
    """

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
        """Data validation"""
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

    def _base_repr(self) -> str:
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

    def __repr__(self) -> str:
        """String representation for iPython"""
        return "**Damage** " + self._base_repr()

    def _repr_html_(self) -> str:
        """HTML representation for Jupyter notebook"""
        return "<b>Damage</b> " + self._base_repr()

    @staticmethod
    def simplify(damages: Iterable[Damage], /) -> list[Damage]:
        """Attempt to reduce multiple Damage instances to a shorter form.

        Only compatible damage types are combined; e.g. slashing + fire will
        remain separate, as will direct fire damage and splash fire damage.

        This method is typically called automatically.

        **Example:**

        >>> Damage.simplify([Damage("fire", 1, 6), Damage("fire", 1, 6, 4)])
        [**Damage** 2d6+4 fire]
        """
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
        r"""Create a deep copy of this instance, changing one or more parameters.

        :param \*\*kwargs:
            Any of the :class:`Damage` parameters.

        e.g. a longsword with :prd_feats:`Inventive Offensive <989>`
        adding ``deadly d6``:

        >>> Damage("slashing", 1, 8).copy(deadly=6)
        **Damage** 1d8 slashing deadly d6
        """
        kwargs2 = {k: getattr(self, k) for k in self.__annotations__}
        kwargs2.update(kwargs)
        return Damage(**kwargs2)

    def hands(self, hands: Literal[1, 2]) -> Damage:
        """Specify how many hands are used to wield the weapon.

        You should always call this method explicitly for weapons with
        either the `two-hands` or the `fatal aim` traits.
        """
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
        """Reduce the damage die size by 1 step.

        e.g. a +1 Striking Maul with :prd_feats:`Grasping Reach <4493>`:

        >>> Damage("bludgeoning", 2, 12).reduce_die()
        **Damage** 2d10 bludgeoning
        """
        return self.copy(faces=self.faces - 2)

    def increase_die(self) -> Damage:
        """Increase the damage die size by 1 step.

        e.g. a Dagger with :prd_feats:`Deadly Simplicity <4642>`:

        >>> Damage("piercing", 1, 4).increase_die()
        **Damage** 1d6 piercing
        """
        return self.copy(faces=self.faces + 2)

    def vicious_swing(self, dice: int = 1) -> Damage | ExpandedDamage:
        """:prd_feats:`Vicious Swing <4775>`, a.k.a. Power Attack, and similar effects.

        Add extra weapon dice, which impact the fatal trait but
        not the deadly trait.

        :param int dice:
            Number of extra weapon dice to add. Default: 1
        :returns:
            :class:`Damage` or :class:`ExpandedDamage`

        **Note**

        This is not the same as just adding a damage die. Observe the difference:

        - A +2 Striking Glaive with Vicious Swing, which deals 3d8
          damage on a hit and an extra d8 on a critical hit:

          >>> Damage("slashing", 2, 8, deadly=8).vicious_swing()
          **Critical success** (3d8)x2 slashing plus 1d8 slashing
          **Success** 3d8 slashing

        - A +2 Greater Striking Glaive, which deals 3d8 damage on a hit
          and an extra 2d8 on a critical hit:

          >>> Damage("slashing", 3, 8, deadly=8).expand()
          **Critical success** (3d8)x2 slashing plus 2d8 slashing
          **Success** 3d8 slashing
        """
        if self.deadly:
            return self + {
                DoS.critical_success: [
                    Damage(self.type, dice, self.fatal or self.faces, multiplier=2)
                ],
                DoS.success: [Damage(self.type, dice, self.faces)],
            }
        return self.copy(dice=self.dice + dice)

    def expand(self) -> ExpandedDamage:
        """Convert this :class:`Damage` instance to an
        :class:`ExpandedDamage`.

        This resolves the `two-hands`, `deadly`, `fatal`, and `fatal_aim`
        traits, as well as applying the success profile for weapon strikes
        (``basic_save=False``), spells with a basic saving throw (``basic_save=True``),
        and splash damage.

        You typically don't need to call this method explicitly.
        """
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

    @overload
    def __add__(self, other: Damage | Iterable[Damage]) -> DamageList: ...
    @overload
    def __add__(self, other: ExpandedDamageLike) -> ExpandedDamage: ...

    def __add__(self, other: DamageLike) -> DamageList | ExpandedDamage:
        """Add two damage specs together"""
        d = self._auto_two_hands()
        return DamageList([d]) + other


class DamageList(UserList[Damage]):
    """Output of the addition of :class:`Damage`.

    This class should never be initialised directly; it is returned by applying
    the ``+`` operator to two or more :class:`Damage` objects.
    """

    @property
    def basic_save(self) -> bool:
        return self[0].basic_save

    def _base_repr(self) -> str:
        return " plus ".join(el._base_repr() for el in self)

    def __repr__(self) -> str:
        """String representation for iPython"""
        return "**Damage** " + self._base_repr()

    def _repr_html_(self) -> str:
        """HTML representation for Jupyter notebook"""
        return "<b>Damage</b> " + self._base_repr()

    def expand(self) -> ExpandedDamage:
        """Convert :class:`DamageList` to :class:`ExpandedDamage`."""
        return ExpandedDamage.sum(self)

    def simplify(self) -> DamageList:
        """See :meth:`Damage.simplify`."""
        return DamageList(Damage.simplify(self))

    @overload  # type: ignore[override]
    def __add__(self, other: Damage | Iterable[Damage]) -> DamageList: ...
    @overload
    def __add__(self, other: ExpandedDamageLike) -> ExpandedDamage: ...

    def __add__(self, other: DamageLike) -> DamageList | ExpandedDamage:
        if isinstance(other, Damage):
            other = [other]
        if not isinstance(other, Mapping):
            return DamageList([*self, *other]).simplify()
        return self.expand() + other

    __iadd__ = __add__


class ExpandedDamage(UserDict[DoS, list[Damage]]):
    """Expanded damage specification.

    This can be either generated by calling :meth:`Damage.expand` or
    by manually building a complex damage profile, which doesn't
    need to respect the rules for weapon strikes or basic saving throws.

    :param data:
        A :class:`Damage`, a sequence of :class:`Damage`, or
        a mapping of :class:`DoS` to lists of :class:`Damage`.

        In the latter case, you need to explicitly specify what happens
        on each roll outcome; you cannot use the `basic_save`, `deadly`,
        `fatal`, or `fatal_aim` attributes.
        Omitted outcomes deal no damage.

    You can also initialize this class by adding a plain dict of ``{DoS:[Damage]}``
    to a :class:`Damage` object.

    **Examples**

    A :prd_equipment:`Flaming <2838>` rune adds 1d6 fire to your weapon, with an
    additional 1d10 persistent fire on a critical hit. The 1d6 can be expressed with a
    simple :class:`Damage`, but the extra effect on the critical hit can't.

    A *+1 Striking Flaming Rapier* can be defined as:

    >>> Damage("piercing", 2, 6, deadly=8) + Damage("fire", 1, 6) + {
    ...     DoS.critical_success: [Damage("fire", 1, 10, persistent=True)]
    ... }
    **Critical success** (2d6)x2 piercing plus 1d8 piercing plus (1d6)x2 fire
    plus 1d10 persistent fire
    **Success** 2d6 piercing plus 1d6 fire

    Above we implicitly initialized an :class:`ExpandedDamage` by auto-expanding the
    `deadly` trait by adding a dict to a :class:`Damage` object.
    The above is equivalent to:

    >>> rapier = ExpandedDamage({
    ...     DoS.success: [Damage("piercing", 2, 6)],
    ...     DoS.critical_success: [
    ...         Damage("piercing", 2, 6, multiplier=2),
    ...         Damage("piercing", 1, 8),
    ...     ],
    ... })
    >>> flaming = ExpandedDamage({
    ...     DoS.success: [Damage("fire", 1, 6)],
    ...     DoS.critical_success: [
    ...         Damage("fire", 1, 6, multiplier=2),
    ...         Damage("fire", 1, 10, persistent=True),
    ...     ],
    ... })
    >>> rapier + flaming
    **Critical success** (2d6)x2 piercing plus 1d8 piercing plus (1d6)x2 fire
    plus 1d10 persistent fire
    **Success** 2d6 piercing plus 1d6 fire

    Which is the same as writing:

    >>> ExpandedDamage({
    ...     DoS.success: [
    ...         Damage("piercing", 2, 6),
    ...         Damage("fire", 1, 6),
    ...     ],
    ...     DoS.critical_success: [
    ...         Damage("piercing", 2, 6, multiplier=2),
    ...         Damage("piercing", 1, 8),
    ...         Damage("fire", 1, 6, multiplier=2),
    ...         Damage("fire", 1, 10, persistent=True),
    ...     ],
    ... })
    **Critical success** (2d6)x2 piercing plus 1d8 piercing plus (1d6)x2 fire
    plus 1d10 persistent fire
    **Success** 2d6 piercing plus 1d6 fire

    What if the reapier was used for a swashbuckler's
    :prd_actions:`Confident Finisher <2818>`, which adds 2d6
    precision damage, and half as much on a failure?

    >>> p = Damage("precision", 2, 6)
    >>> finisher = {
    ...     DoS.failure: [p.copy(multiplier=0.5)],
    ...     DoS.success: [p],
    ...     DoS.critical_success: [p.copy(multiplier=2)],
    ... }
    >>> rapier + flaming + finisher
    **Critical success** (2d6)x2 piercing plus 1d8 piercing plus (1d6)x2 fire
    plus (2d6)x2 precision plus 1d10 persistent fire
    **Success** 2d6 piercing plus 1d6 fire plus 2d6 precision
    **Failure** (2d6)/2 precision
    """

    def __init__(self, data: DamageLike | None = None, /):
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

    def expand(self) -> ExpandedDamage:
        """Dummy method to match :class:`Damage` and :class:`DamageList` interface."""
        return self

    def __add__(self, other: DamageLike) -> ExpandedDamage:
        return ExpandedDamage.sum([self, other])

    @staticmethod
    def sum(items: Iterable[DamageLike]) -> ExpandedDamage:
        """Sum multiple :class:`Damage` or :class:`ExpandedDamage` objects together."""
        out: dict[DoS, list[Damage]] = {}
        for item in items:
            item = ExpandedDamage(item)
            for k, v in item.items():
                out.setdefault(k, []).extend(v)

        out = {k: Damage.simplify(v) for k, v in out.items()}
        return ExpandedDamage(out)

    def _repr_html_(self) -> str:
        """HTML representation for Jupyter notebook"""
        out = []
        for k, v in self.items():
            name = k.name.replace("_", " ").capitalize()
            out.append(f"<b>{name}</b> {DamageList(v)._base_repr()}")
        return "<br>\n".join(out)

    def __repr__(self) -> str:
        """String representation for iPython"""
        return (
            self._repr_html_()
            .replace("<b>", "**")
            .replace("</b>", "**")
            .replace("<br>", "")
        )

    def to_dict_of_str(self) -> dict[str, str]:
        """Pretty-print as a dict"""
        return {str(k): DamageList(v)._base_repr() for k, v in self.items()}

    def filter(
        self, *which: Literal["direct", "persistent", "splash"]
    ) -> ExpandedDamage:
        """Select only direct and/or persistent and/or splash damage."""
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

    def simplify(self) -> ExpandedDamage:
        """See :meth:`Damage.simplify`."""
        return ExpandedDamage({k: DamageList(v).simplify() for k, v in self.items()})


ExpandedDamageLike: TypeAlias = (
    ExpandedDamage | Mapping[int, Collection[Damage]] | Mapping[DoS, Collection[Damage]]
)
DamageLike: TypeAlias = Damage | Iterable[Damage] | ExpandedDamageLike
