"""Configuration values that define slider ranges and default scaling for the UI."""

from dataclasses import dataclass

@dataclass(frozen=True)
class OrbelConfig:
    """Configuration values that determine slider ranges and defaults for both views."""
    rel_a_min: float = 0.5
    rel_a_max: float = 2.35
    abs_a_min: float = 1.0
    abs_a_max: float = 3.53
    a_frac_min: float = 0.10
    a_frac_max: float = 1.00
    default_a_frac: float = 0.35

DEFAULT_CONFIG = OrbelConfig()