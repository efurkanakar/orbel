"""Configure Matplotlib figures and axes for consistent 3D/2D orbit views."""

from __future__ import annotations


def configure_axes(fig3d, fig2d, ax3d, ax2d) -> None:
    """Apply common styling and layout to the 3D and 2D axes."""

    fig3d.patch.set_facecolor("white")
    fig2d.patch.set_facecolor("white")
    fig3d.subplots_adjust(left=-0.02, right=1.02, bottom=-0.03, top=1.03)
    fig2d.subplots_adjust(left=0.08, right=0.96, bottom=0.10, top=0.96)

    # 2D sky-plane view: astrometric offsets on the sky.
    ax2d.set_xlabel("ΔRA")
    ax2d.set_ylabel("ΔDec")

    ax3d.set_facecolor("white")
    ax2d.set_facecolor("white")
    grid_rgba = (0.7, 0.7, 0.7, 0.5)
    for axis in (ax3d.xaxis, ax3d.yaxis, ax3d.zaxis):
        axis._axinfo["grid"]["color"] = grid_rgba

    default_pane_color = (0.94, 0.94, 0.94, 1.0)
    for pane in (ax3d.xaxis.pane, ax3d.yaxis.pane, ax3d.zaxis.pane):
        pane.set_facecolor(default_pane_color)

    ax3d.set_xlabel("North", labelpad=10)
    ax3d.set_ylabel("East", labelpad=10)
    ax3d.set_zlabel("LoS", labelpad=10)

    ax2d.set_aspect("equal", adjustable="box")
    ax3d.set_box_aspect((1, 1, 1))
    try:
        ax3d.set_proj_type("ortho")
    except Exception:
        # Fallback for Matplotlib versions without set_proj_type
        pass
    ax3d.set_autoscale_on(False)
    ax2d.set_autoscale_on(False)
