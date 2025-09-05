from pathfinder2e_stats.armory._common import _weapon

__all__ = (
    "dueling_sword",
    "grindblade",
    "nano_edge_rapier",
    "phase_cutlass",
    "plasma_sword",
    "puzzleblade",
)

dueling_sword = _weapon("dueling_sword", "slashing", 8)
grindblade = _weapon("grindblade", "slashing", 8, fatal=12, critical="knife")
nano_edge_rapier = _weapon("nano_edge_rapier", "piercing", 6, deadly=8)
phase_cutlass = _weapon("phase_cutlass", "slashing", 6, deadly=6)
plasma_sword = _weapon("plasma_sword", "fire", 8, critical="plasma")
puzzleblade = _weapon("puzzleblade", "slashing", 8)
