"""Static tooltip text and option specifications used by the control panel."""

from __future__ import annotations

from .panels import OptionSpec


parameter_tooltips = {
    "a": (
        "Semi-major axis (shared): sets the orbit size used by BOTH views. "
        "In the relative view it scales the relative ellipse; in the absolute "
        "view it is the system semi-major axis (a = a1 + a2). Changing a "
        "rescales the axes and updates the mean motion via Kepler's law: "
        "n = sqrt((m1 + m2) / a^3)."
    ),
    "e": (
        "Eccentricity: a dimensionless measure of how much the orbit deviates "
        "from a circle. Defined as the ratio between the distance of the foci "
        "and the major axis."
    ),
    "m1": (
        "Primary component mass: the dominant component in the system (or the "
        "binary when dealing with hierarchical triples)."
    ),
    "m2": (
        "Secondary component mass: the companion orbiting the primary "
        "(or tertiary body in a triple)."
    ),
    "i": (
        "Inclination: tilt of the orbital plane relative to the sky plane. "
        "0° is face-on, 90° is edge-on, >90° is retrograde."
    ),
    "Om": (
        "Longitude of the ascending node: angle on the sky from celestial "
        "north to the ascending node, measured counter-clockwise."
    ),
    "w": (
        "Argument of periastron: angle measured along the orbit from the "
        "ascending node to periastron inside the orbital plane."
    ),
}

option_specs = (
    OptionSpec("show_nodes", "Show nodes"),
    OptionSpec("show_line_nodes", "Show line of nodes"),
    OptionSpec("show_sky_plane", "Show sky plane"),
    OptionSpec("show_axis_triad", "Show axis triad"),
    OptionSpec("show_Omega", "Show <i>Ω</i> arc"),
    OptionSpec("show_centers", "Show central markers"),
    OptionSpec("show_omega", "Show <i>ω</i> arc"),
    OptionSpec("show_peri_link", "Show periastron link"),
    OptionSpec("show_inclination", "Show <i>i</i> wedge"),
    OptionSpec("show_bodies", "Show bodies"),
)

__all__ = ["parameter_tooltips", "option_specs"]