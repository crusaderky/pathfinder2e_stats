from pathfinder2e_stats.damage_spec import Damage


def gluon(level: int = 6) -> Damage:
    faces = min(level, 15) // 3 * 2
    return Damage("bleed", 1, faces, persistent=True)


def graviton(type: str = "bludgeoning") -> Damage:
    return Damage(type, 1, 6)


def photon() -> Damage:
    return Damage("fire", 1, 6)
