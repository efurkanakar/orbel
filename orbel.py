import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QGroupBox, QFrame,
    QLabel, QSlider, QDoubleSpinBox, QPushButton,
    QSizePolicy, QTabBar, QStackedLayout, QMessageBox, QAction
)
from PyQt5.QtCore import Qt, QTimer, QLocale, QSize, QPointF, QEvent, QCoreApplication
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QPolygonF, QIcon, QFont

import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import proj3d


def Rz(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[ c, -s, 0],
                     [ s,  c, 0],
                     [ 0,  0, 1]])

def Rx(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[1, 0, 0],
                     [0, c,-s],
                     [0, s,  c]])

def solve_kepler(M, e, tol=1e-12, n_iter=40):
    E = M + e*np.sin(M)
    for _ in range(n_iter):
        f  = E - e*np.sin(E) - M
        fp = 1.0 - e*np.cos(E)
        dE = f/fp
        E -= dE
        if np.all(np.abs(dE) < tol):
            break
    return E

def E_from_nu(nu, e):
    return 2.0*np.arctan2(np.sqrt(1-e)*np.sin(nu/2.0), np.sqrt(1+e)*np.cos(nu/2.0))

def M_from_E(E, e):
    return E - e*np.sin(E)

def nu_from_E(E, e):
    return 2.0*np.arctan2(np.sqrt(1+e)*np.sin(E/2.0), np.sqrt(1-e)*np.cos(E/2.0))

class LegendIcon(QWidget):
    def __init__(self, kind, parent=None):
        super().__init__(parent)
        self.kind = kind
        self.setFixedSize(18, 18)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        C0 = QColor("#1f77b4")
        C1 = QColor("#ff7f0e")
        gray = QColor("#9ca3af")
        gold = QColor("#facc15")
        blue = QColor("dodgerblue")
        red  = QColor("firebrick")
        black = QColor("#000000")

        w, h = self.width(), self.height()
        cx, cy = w/2, h/2
        r = min(w, h)*0.35

        if self.kind == "periastron":
            pts = [(cx, cy-r), (cx+r, cy), (cx, cy+r), (cx-r, cy)]
            poly = QPolygonF([QPointF(x, y) for x, y in pts])
            p.setPen(QPen(QColor("#cbd5e1"), 1))
            p.setBrush(QBrush(gold))
            p.drawPolygon(poly)

        elif self.kind == "asc":
            pts = [(cx, cy-r), (cx+r, cy+r), (cx-r, cy+r)]
            poly = QPolygonF([QPointF(x, y) for x, y in pts])
            p.setPen(QPen(blue, 1))
            p.setBrush(QBrush(blue))
            p.drawPolygon(poly)

        elif self.kind == "des":
            pts = [(cx-r, cy-r), (cx+r, cy-r), (cx, cy+r)]
            poly = QPolygonF([QPointF(x, y) for x, y in pts])
            p.setPen(QPen(red, 1))
            p.setBrush(QBrush(red))
            p.drawPolygon(poly)

        elif self.kind == "nodes":
            p.setPen(QPen(gray, 2, Qt.DashLine))
            p.drawLine(int(w*0.15), int(cy), int(w*0.85), int(cy))

        elif self.kind == "star":
            p.translate(cx, cy)
            p.setPen(QPen(black, 1.0))
            p.setBrush(QBrush(black))
            outer = r
            inner = r*0.45
            pts = []
            for k in range(10):
                ang = -np.pi/2 + k*np.pi/5
                rad = outer if k % 2 == 0 else inner
                pts.append(QPointF(rad*np.cos(ang), rad*np.sin(ang)))
            p.drawPolygon(QPolygonF(pts))

        elif self.kind == "bodies":
            p.setPen(QPen(QColor("#cbd5e1"), 1))
            p.setBrush(QBrush(QColor("navy")));
            p.drawEllipse(int(cx - 6), int(cy - 5), 10, 10)
            p.setBrush(QBrush(QColor("darkred")));
            p.drawEllipse(int(cx + 2), int(cy - 5), 10, 10)

        p.end()

def legend_row(text, kind):
    row = QWidget()
    lay = QHBoxLayout(row)
    lay.setContentsMargins(0,0,0,0)
    lay.setSpacing(8)
    ico = LegendIcon(kind)
    lbl = QLabel(text)
    lbl.setTextFormat(Qt.RichText)
    f = lbl.font(); f.setPointSize(10)
    lbl.setFont(f)
    lay.addWidget(ico, 0)
    lay.addWidget(lbl, 1)
    return row

class OrbitCanvasBase:
    def __init__(self, title3d="3-D Orbit Geometry", title2d="Sky-Plane Projection"):
        plt.style.use("default")
        plt.rcParams.update({
            "font.size": 11,
            "axes.titlesize": 12,
            "axes.labelsize": 11,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
        })

        self.card3d = QGroupBox(title3d); self.card3d.setObjectName("plotCard")
        lay3d = QVBoxLayout(self.card3d); lay3d.setContentsMargins(8,8,8,6); lay3d.setSpacing(6)
        self.fig3d = Figure(dpi=96)
        self.canvas3d = FigureCanvas(self.fig3d)
        self.canvas3d.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.card3d.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        lay3d.addWidget(self.canvas3d, 1)
        self.toolbar3d = NavigationToolbar(self.canvas3d, self.card3d)
        self.toolbar3d.setIconSize(QSize(16,16))
        lay3d.addWidget(self.toolbar3d, 0)
        self.ax3d = self.fig3d.add_subplot(111, projection="3d")

        self.card2d = QGroupBox(title2d); self.card2d.setObjectName("plotCard")
        lay2d = QVBoxLayout(self.card2d); lay2d.setContentsMargins(8,8,8,6); lay2d.setSpacing(6)
        self.fig2d = Figure(dpi=96)
        self.canvas2d = FigureCanvas(self.fig2d)
        self.canvas2d.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.card2d.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        lay2d.addWidget(self.canvas2d, 1)
        self.toolbar2d = NavigationToolbar(self.canvas2d, self.card2d)
        self.toolbar2d.setIconSize(QSize(16,16))
        lay2d.addWidget(self.toolbar2d, 0)

        self.fig3d.patch.set_facecolor("white")
        self.fig2d.patch.set_facecolor("white")
        self.fig3d.subplots_adjust(left=0.01, right=0.995, bottom=0.02, top=0.995)
        self.fig2d.subplots_adjust(left=0.08, right=0.96, bottom=0.10, top=0.96)

        self.ax2d = self.fig2d.add_subplot(111)
        self.ax3d.set_facecolor("white"); self.ax2d.set_facecolor("white")
        try:
            for pane in (self.ax3d.xaxis.pane, self.ax3d.yaxis.pane, self.ax3d.zaxis.pane):
                pane.set_facecolor((1,1,1,0.0))
        except Exception:
            pass

        self.ax2d.invert_xaxis()
        self.ax2d.set_aspect('equal', adjustable='box')
        self.ax3d.set_box_aspect((1,1,1))
        try: self.ax3d.set_proj_type("ortho")
        except Exception: pass
        self.ax3d.set_autoscale_on(False); self.ax2d.set_autoscale_on(False)

        self.init_elev, self.init_azim = 20, -60
        self.ax3d.view_init(elev=self.init_elev, azim=self.init_azim)

        self.center3d = self.ax3d.scatter(0,0,0, marker="*", c="black", s=80, zorder=6)
        self.center2d = self.ax2d.scatter(0,0,   marker="*", c="black", s=80, zorder=6)


        self._axis_texts = {
            "North": self.ax3d.text2D(0, 0, "North", transform=self.ax3d.transAxes,
                                      fontsize=11, ha="center", va="center"),
            "East": self.ax3d.text2D(0, 0, "East", transform=self.ax3d.transAxes,
                                     fontsize=11, ha="center", va="center"),
            "LoS": self.ax3d.text2D(0, 0, "LoS", transform=self.ax3d.transAxes,
                                    fontsize=11, ha="center", va="center"),
        }

        self.canvas3d.mpl_connect("draw_event", lambda evt: self._place_axis_labels())

        self._ne_lines = None  # (lineE, lineN, labelE, labelN)

        self.i_wedge = Poly3DCollection([], facecolor="cyan", alpha=0.30, edgecolor="none", zorder=4)
        self.ax3d.add_collection3d(self.i_wedge)

        self.sky_plane = Poly3DCollection([], facecolor="#3b82f6", alpha=0.06, edgecolor="none", zorder=1)
        self.ax3d.add_collection3d(self.sky_plane)

        (self.orbit3d,) = self.ax3d.plot([], [], [], "k", lw=1.25, zorder=2)
        (self.orbit2d,) = self.ax2d.plot([], [],     "k", lw=1.25, zorder=2)
        self.nodes3d, = self.ax3d.plot([], [], [], "--", color="gray", lw=1.1, alpha=0.7, zorder=3)
        self.nodes2d, = self.ax2d.plot([], [],     "--", color="gray", lw=1.1, alpha=0.7, zorder=3)
        self.asc3d, = self.ax3d.plot([], [], [], "^", color="dodgerblue", ms=8, zorder=7)
        self.des3d, = self.ax3d.plot([], [], [], "v", color="firebrick",  ms=8, zorder=7)
        self.asc2d, = self.ax2d.plot([], [],     "^", color="dodgerblue", ms=8, zorder=7)
        self.des2d, = self.ax2d.plot([], [],     "v", color="firebrick",  ms=8, zorder=7)
        self.peri3d, = self.ax3d.plot([], [], [], "d", color="gold", ms=8, zorder=8)
        self.peri2d, = self.ax2d.plot([], [],     "d", color="gold", ms=8, zorder=8)

        self.Om_arc3d, = self.ax3d.plot([], [], [], color="seagreen",   lw=2.0, zorder=9)
        self.Om_arc2d, = self.ax2d.plot([], [],     color="seagreen",   lw=2.0, zorder=9)
        self.w_arc3d,  = self.ax3d.plot([], [], [], color="darkorange", lw=2.0, zorder=10)
        self.w_arc2d,  = self.ax2d.plot([], [],     color="darkorange", lw=2.0, zorder=10)

        self.body3d = self.ax3d.scatter([0],[0],[0], c="purple", s=32, zorder=11)
        self.body2d = self.ax2d.scatter([0],[0],     c="purple", s=32, zorder=11)

        self.init = dict(a=1.0, e=0.5,
                         i=np.deg2rad(45.0),
                         w=np.deg2rad(90.0),
                         Om=np.deg2rad(90.0),
                         m1=1.2, m2=0.8,
                         start_nu=np.deg2rad(45.0))
        self.a = self.init["a"]; self.e = self.init["e"]
        self.i = self.init["i"]; self.w = self.init["w"]; self.Om = self.init["Om"]
        self.m1 = self.init["m1"]; self.m2 = self.init["m2"]
        self.start_nu = self.init["start_nu"]

        self.dM = 0.020

        self.nu = float(self.start_nu)
        E0 = E_from_nu(self.nu, self.e)
        self.M = float(M_from_E(E0, self.e))

        self.timer = QTimer(); self.timer.setInterval(15)
        self.timer.timeout.connect(self._step)

        self._L = 1.6
        self.ax2d.grid(True, which="both", linestyle=":", alpha=0.25, linewidth=0.8)


    def _redraw(self):
        self.canvas3d.draw_idle()
        self.canvas2d.draw_idle()

    def _rotmat(self): return Rz(self.Om) @ Rx(self.i) @ Rz(self.w)

    def _orbital_xyz_rel(self, f):
        r = self.a*(1 - self.e**2) / (1 + self.e*np.cos(f))
        x, y = r*np.cos(f), r*np.sin(f)
        return (self._rotmat() @ np.vstack((x, y, np.zeros_like(x))))

    def _update_NE_guides(self):
        if getattr(self, "_ne_lines", None) is None:
            lineE, = self.ax2d.plot([], [], '-', color='0.45', alpha=0.35, lw=1.0, zorder=1)
            lineN, = self.ax2d.plot([], [], '-', color='0.45', alpha=0.35, lw=1.0, zorder=1)
            labE   = self.ax2d.text(0, 0, "E", ha="right", va="center", fontsize=9, color='0.25', alpha=0.9, zorder=2)
            labN   = self.ax2d.text(0, 0, "N", ha="center", va="bottom", fontsize=9, color='0.25', alpha=0.9, zorder=2)
            self._ne_lines = (lineE, lineN, labE, labN)
        L = self._L
        lineE, lineN, labE, labN = self._ne_lines
        lineE.set_data([-L, L], [0,0])
        lineN.set_data([0,0], [-L, L])
        labN.set_position((0, 0.92*L))
        labE.set_position((0.92*L, 0))

    def _proj_axes_xy(self, x, y, z):
        X2, Y2, _ = proj3d.proj_transform(x, y, z, self.ax3d.get_proj())
        x_disp, y_disp = self.ax3d.transData.transform((X2, Y2))
        ax_x, ax_y = self.ax3d.transAxes.inverted().transform((x_disp, y_disp))
        return ax_x, ax_y

    def _place_axis_labels(self):
        L = self._L
        ln = getattr(self, "_arrow_len", 0.90 * L)
        pad = 0.15 * L
        tips = {
            "North": (ln + pad, 0.0, 0.0),
            "East": (0.0, ln + pad, 0.0),
            "LoS": (0.0, 0.0, ln + pad),
        }
        for lbl, (x, y, z) in tips.items():
            axx, axy = self._proj_axes_xy(x, y, z)
            # görünür alan dışına taşmasın
            axx = min(max(axx, -0.05), 1.05)
            axy = min(max(axy, -0.05), 1.05)
            self._axis_texts[lbl].set_position((axx, axy))

    def _update_axes_limits(self, margin=1.05):
        Rmax = max(0.1, self.a*(1+self.e))
        L = margin*Rmax
        self._L = L
        self.ax3d.set(xlim=(-L,L), ylim=(-L,L), zlim=(-L,L))
        self.ax2d.set(xlim=( L,-L), ylim=(-L, L))

        plane = [(-L,-L,0.0), ( L,-L,0.0), ( L, L,0.0), (-L, L,0.0)]
        self.sky_plane.set_verts([np.array(plane)])

        for q in getattr(self, "_ref_quivers", []):
            try: q.remove()
            except Exception: pass
        self._ref_quivers = []
        arrow_len = 0.90 * L
        arrow_kwargs = dict(color="gray", arrow_length_ratio=0.07, lw=1,
                            length=arrow_len, normalize=True)
        for u in [(1,0,0),(0,1,0),(0,0,1)]:
            self._ref_quivers.append(self.ax3d.quiver(0,0,0,*u,**arrow_kwargs))

        self._arrow_len = arrow_len
        self._place_axis_labels()
        self._update_NE_guides()

    def _update_nodes(self):
        t = np.array([-0.9*self._L, 0.9*self._L])
        x_nd = t*np.cos(self.Om); y_nd = t*np.sin(self.Om)
        self.nodes3d.set_data(x_nd, y_nd); self.nodes3d.set_3d_properties(np.zeros_like(t))
        self.nodes2d.set_data(-y_nd, x_nd)

    def _update_Om_arc(self):
        Om = self.Om % (2*np.pi)
        if Om < 1e-9:
            self.Om_arc3d.set_data([], []); self.Om_arc3d.set_3d_properties([])
            self.Om_arc2d.set_data([], [])
            return
        th = np.linspace(0, (2*np.pi if abs(Om-2*np.pi) < 1e-9 else Om), 200, endpoint=True)
        r = 0.7*self._L
        xO, yO = r*np.cos(th), r*np.sin(th)
        self.Om_arc3d.set_data(xO, yO); self.Om_arc3d.set_3d_properties(np.zeros_like(th))
        self.Om_arc2d.set_data(-yO, xO)

    def _omega_arc_points(self, w):
        dir_sign = +1.0 if self.i < (0.5*np.pi) else -1.0
        f_asc = (-w) % (2*np.pi) if dir_sign > 0 else (w % (2*np.pi))
        th = np.linspace(0, w, 200, endpoint=True)
        f_arc = (f_asc + dir_sign*th) % (2*np.pi)
        return f_arc

    def _dir_sign(self):
        return +1.0 if self.i < (0.5*np.pi) else -1.0

    def _recompute_from_M(self):
        E = solve_kepler(self.M, self.e)
        self.nu = float(nu_from_E(E, self.e))

    def _set_nu_keep_phase(self, nu_new):
        self.nu = float(nu_new)
        E = E_from_nu(self.nu, self.e)
        self.M = float(M_from_E(E, self.e))

    def start(self):
        if not self.timer.isActive(): self.timer.start()
    def stop(self):
        if self.timer.isActive(): self.timer.stop()
    def _step(self):
        self.M += self._dir_sign() * self.dM
        self._recompute_from_M()
        self._update_body_only()
        self._redraw()

    def update_all(self): raise NotImplementedError
    def _update_body_only(self): raise NotImplementedError

class RelativeCanvas(OrbitCanvasBase):
    def __init__(self):
        super().__init__(title3d="3-D Orbit Geometry", title2d="Sky-Plane Projection")
        self.update_all()

    def _update_orbit_curves(self):
        X,Y,Z = self._orbital_xyz_rel(np.linspace(0, 2*np.pi, 1000))
        self.orbit3d.set_data(X, Y); self.orbit3d.set_3d_properties(Z)
        self.orbit2d.set_data(-Y, X)

    def _update_periastron_ascdesc(self):
        Xp,Yp,Zp = self._orbital_xyz_rel(np.array([0.0]))
        self.peri3d.set_data([Xp[0]],[Yp[0]]); self.peri3d.set_3d_properties([Zp[0]])
        self.peri2d.set_data([-Yp[0]],[Xp[0]])
        f_asc = (-self.w) % (2*np.pi) if self.i < np.pi/2 else (self.w % (2*np.pi))
        Xa,Ya,Za = self._orbital_xyz_rel(np.array([f_asc]))
        Xd,Yd,Zd = self._orbital_xyz_rel(np.array([(f_asc + np.pi) % (2*np.pi)]))
        self.asc3d.set_data([Xa[0]],[Ya[0]]); self.asc3d.set_3d_properties([Za[0]])
        self.des3d.set_data([Xd[0]],[Yd[0]]); self.des3d.set_3d_properties([Zd[0]])
        self.asc2d.set_data([-Ya[0]],[Xa[0]])
        self.des2d.set_data([-Yd[0]],[Xd[0]])

    def _update_w_arc(self):
        w = self.w % (2*np.pi)
        if w < 1e-9:
            self.w_arc3d.set_data([], []); self.w_arc3d.set_3d_properties([])
            self.w_arc2d.set_data([], [])
            return
        f_arc = self._omega_arc_points(w)
        Xw,Yw,Zw = self._orbital_xyz_rel(f_arc)
        n = (self._rotmat() @ np.array([0,0,1.0])); eps = 1e-3
        Xw += eps*n[0]; Yw += eps*n[1]; Zw += eps*n[2]
        self.w_arc3d.set_data(Xw, Yw); self.w_arc3d.set_3d_properties(Zw)
        self.w_arc2d.set_data(-Yw, Xw)

    def _update_i_wedge(self):
        k = np.array([0.0, 0.0, 1.0])
        n = self._rotmat() @ k
        axis = np.cross(k, n)
        s = np.linalg.norm(axis)
        if s < 1e-9:
            self.i_wedge.set_verts([]); self.i_wedge.set_alpha(0.0); return
        l_hat = axis/s
        e1 = np.cross(l_hat, k); e1 /= np.linalg.norm(e1)
        ths = np.linspace(0.0, float(self.i), 40)
        rim = np.vstack([np.cos(th)*e1 + np.sin(th)*np.cross(l_hat, e1) for th in ths])
        verts = np.vstack((np.zeros(3), 0.7*self._L*rim))
        self.i_wedge.set_verts([verts]); self.i_wedge.set_alpha(0.30)

    def _update_body_only(self):
        nu = self.nu
        Xb,Yb,Zb = self._orbital_xyz_rel(np.array([nu]))
        self.body3d._offsets3d = (Xb, Yb, Zb)
        self.body2d.set_offsets(np.column_stack((-Yb, Xb)))

    def update_all(self):
        self._update_axes_limits()
        self._update_orbit_curves()
        self._update_nodes()
        self._update_Om_arc()
        self._update_w_arc()
        self._update_periastron_ascdesc()
        self._update_body_only()
        self._update_i_wedge()
        self._redraw()

class AbsoluteCanvas(OrbitCanvasBase):
    def __init__(self):
        super().__init__(title3d="3-D Orbit Geometry", title2d="Projected Orbits")
        self.center3d.remove(); self.center2d.remove()
        self.center3d = self.ax3d.scatter(0,0,0, marker="*", c="black", s=90, zorder=6)
        self.center2d = self.ax2d.scatter(0,0,   marker="*", c="black", s=90, zorder=6)

        (self.orbit1_3d,) = self.ax3d.plot([], [], [], 'navy', lw=1.25, zorder=2)
        (self.orbit2_3d,) = self.ax3d.plot([], [], [], 'darkred', lw=1.25, zorder=2)
        (self.orbit1_2d,) = self.ax2d.plot([], [],     'navy', lw=1.25, zorder=2)
        (self.orbit2_2d,) = self.ax2d.plot([], [],     'darkred', lw=1.25, zorder=2)

        self.body3d.remove(); self.body2d.remove()
        self.body1_3d = self.ax3d.scatter([], [], [], c='navy', s=50, zorder=11)
        self.body2_3d = self.ax3d.scatter([], [], [], c='darkred', s=50, zorder=11)
        self.body1_2d = self.ax2d.scatter([], [],     c='navy', s=50, zorder=11)
        self.body2_2d = self.ax2d.scatter([], [],     c='darkred', s=50, zorder=11)

        self.peri1_3d, = self.ax3d.plot([], [], [], 'd', color='gold', ms=8, zorder=12)
        self.peri2_3d, = self.ax3d.plot([], [], [], 'd', color='gold', ms=8, zorder=12)
        self.peri1_2d, = self.ax2d.plot([], [],     'd', color='gold', ms=8, zorder=12)
        self.peri2_2d, = self.ax2d.plot([], [],     'd', color='gold', ms=8, zorder=12)

        self.update_all()

    def _split_absolute(self, X,Y,Z):
        m1, m2 = self.m1, self.m2
        c1 = -m2/(m1+m2); c2 = m1/(m1+m2)
        return c1*X, c1*Y, c1*Z, c2*X, c2*Y, c2*Z, c1, c2

    def _update_orbit_curves(self):
        f_line = np.linspace(0, 2*np.pi, 1000)
        Xr,Yr,Zr = self._orbital_xyz_rel(f_line)
        X1,Y1,Z1, X2,Y2,Z2, _, _ = self._split_absolute(Xr,Yr,Zr)
        self.orbit1_3d.set_data(X1, Y1); self.orbit1_3d.set_3d_properties(Z1)
        self.orbit2_3d.set_data(X2, Y2); self.orbit2_3d.set_3d_properties(Z2)
        self.orbit1_2d.set_data(-Y1, X1); self.orbit2_2d.set_data(-Y2, X2)

    def _update_periastron(self):
        Xp,Yp,Zp = self._orbital_xyz_rel(np.array([0.0]))
        x1p,y1p,z1p, x2p,y2p,z2p, _, _ = self._split_absolute(Xp,Yp,Zp)
        self.peri1_3d.set_data([x1p[0]],[y1p[0]]); self.peri1_3d.set_3d_properties([z1p[0]])
        self.peri2_3d.set_data([x2p[0]],[y2p[0]]); self.peri2_3d.set_3d_properties([z2p[0]])
        self.peri1_2d.set_data([-y1p[0]],[x1p[0]]); self.peri2_2d.set_data([-y2p[0]],[x2p[0]])

    def _update_w_arc(self):
        w = self.w % (2*np.pi)
        if w < 1e-9:
            self.w_arc3d.set_data([], []); self.w_arc3d.set_3d_properties([])
            self.w_arc2d.set_data([], [])
            return
        f_arc = self._omega_arc_points(w)
        Xw,Yw,Zw = self._orbital_xyz_rel(f_arc)
        scale = self.m1/(self.m1+self.m2)
        Xw *= scale; Yw *= scale; Zw *= scale
        n = (self._rotmat() @ np.array([0,0,1.0])); eps = 1e-3
        Xw += eps*n[0]; Yw += eps*n[1]; Zw += eps*n[2]
        self.w_arc3d.set_data(Xw, Yw); self.w_arc3d.set_3d_properties(Zw)
        self.w_arc2d.set_data(-Yw, Xw)

    def _update_i_wedge(self):
        k = np.array([0.0, 0.0, 1.0])
        n = self._rotmat() @ k
        axis = np.cross(k, n)
        s = np.linalg.norm(axis)
        if s < 1e-9:
            self.i_wedge.set_verts([]); self.i_wedge.set_alpha(0.0); return
        l_hat = axis/s
        e1 = np.cross(l_hat, k); e1 /= np.linalg.norm(e1)
        ths = np.linspace(0.0, float(self.i), 40)
        rim = np.vstack([np.cos(th)*e1 + np.sin(th)*np.cross(l_hat, e1) for th in ths])
        verts = np.vstack((np.zeros(3), 0.7*self._L*rim))
        self.i_wedge.set_verts([verts]); self.i_wedge.set_alpha(0.30)

    def _update_body_only(self):
        nu = self.nu
        Xr,Yr,Zr = self._orbital_xyz_rel(np.array([nu]))
        x1,y1,z1, x2,y2,z2, _, _ = self._split_absolute(Xr,Yr,Zr)
        self.body1_3d._offsets3d = (x1,y1,z1)
        self.body2_3d._offsets3d = (x2,y2,z2)
        self.body1_2d.set_offsets(np.column_stack((-y1, x1)))
        self.body2_2d.set_offsets(np.column_stack((-y2, x2)))

    def update_all(self):
        self._update_axes_limits()
        self._update_orbit_curves()
        self._update_nodes()
        self._update_Om_arc()
        self._update_w_arc()
        self._update_periastron()
        self._update_body_only()
        self._update_i_wedge()
        self._redraw()

SLIDER_QSS = """
QSlider::groove:horizontal { height: 6px; background: #e5e7eb; border-radius: 3px; }
QSlider::sub-page:horizontal { background: #374151; border-radius: 3px; }
QSlider::handle:horizontal { width: 14px; height: 14px; margin: -5px 0;
    border: 1px solid #111827; border-radius: 7px; background: #ffffff; }
QSlider::handle:horizontal:hover { border: 1px solid #0f172a; }
QSlider::handle:horizontal:pressed { width: 16px; height: 16px; }
"""

UI_QSS = """
QWidget { font-size: 12px; color: #111827; }

QGroupBox {
    background: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    margin-top: 8px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    top: -4px;
    padding: 3 6px;
    color: #111827;
    font-weight: 400;   /* font-size BURAYA değil! */
}

QGroupBox#paramsCard,
QGroupBox#legendBox,
QGroupBox#plotCard {
    font-size: 12pt;    
    font-weight: 400;  
    margin-top: 12px;  
}


QDoubleSpinBox { background: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px;
    padding: 2px 6px; min-height: 24px; min-width: 56px; }
QDoubleSpinBox:focus { border: 1px solid #111827; }


QPushButton#primaryBtn { background: #111827; color: #ffffff; border: none; border-radius: 6px;
    padding: 6px 12px; min-width: 86px; font-weight: 600; }
QPushButton#primaryBtn:hover { background: #0f172a; }
QPushButton#primaryBtn:pressed { background: #0b1220; }

QPushButton#ghostBtn { background: transparent; color: #111827; border: 1px solid #9ca3af;
    border-radius: 6px; padding: 6px 12px; min-width: 86px; font-weight: 600; }
QPushButton#ghostBtn:hover { background: #f3f4f6; }


#ctrlPanel QWidget#paramRow { background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 6px; padding: 6px 8px; }

QGroupBox#plotCard { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; }


QTabBar { qproperty-drawBase: 0; }
QTabBar::tab {
    background: #fafafa;         
    color: #111827;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    padding: 8px 5px;          
    margin: 4px 2px;              
    min-width: 100px;              
    min-height: 5px;               
    font-size: 12px;
    font-weight: 600;
}
QTabBar::tab:hover {
    background: #f3f4f6;
    border-color: #cbd5e1;
}
QTabBar::tab:selected {
    background: #ffffff;
    color: #111827;
    border: 1px solid #374151;     
}
QTabBar::tab:!selected {
    border-color: #e5e7eb;
}
QMenuBar {
    background-color: #f3f4f6;
    color: #111827;
    font-weight: 400;
}
QMenuBar::item {
    background: transparent;
    padding: 4px 10px;
}
QMenuBar::item:selected {
    background: #e5e7eb;
}
QMenu {
    background-color: #ffffff;
    border: 1px solid #d1d5db;
}
QMenu::item:selected {
    background-color: #f3f4f6;
}
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("orbel")
        self.setWindowIcon(QIcon("icons/orbel.ico"))
        self.resize(1700, 760)
        self.setStyleSheet(UI_QSS + SLIDER_QSS)

        menubar = self.menuBar()
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        root = QWidget(self); self.setCentralWidget(root)
        outer = QHBoxLayout(root)
        outer.setContentsMargins(10,10,10,10)
        outer.setSpacing(10)

        left_col = QWidget(); left_col.setObjectName("ctrlPanel")
        left_v = QVBoxLayout(left_col); left_v.setContentsMargins(0,0,0,0); left_v.setSpacing(10)

        self.left_top_spacer = QWidget(); self.left_top_spacer.setFixedHeight(0)
        left_v.addWidget(self.left_top_spacer, 0)

        params_group = QGroupBox("Orbit Parameters")
        params_group.setObjectName("paramsCard")

        params_v = QVBoxLayout(params_group); params_v.setContentsMargins(10,10,10,10); params_v.setSpacing(10)

        def make_pair(box_title, items, slider_len=150):
            box = QGroupBox(box_title)
            inner = QVBoxLayout(box); inner.setContentsMargins(12,10,12,10); inner.setSpacing(10)
            ctrls = []
            for key, label_html, mn, mx, st, init, dec in items:
                cell = QWidget(); cell.setObjectName("paramRow")
                cl = QHBoxLayout(cell); cl.setContentsMargins(8,6,8,6); cl.setSpacing(10)

                lbl_w = QLabel(label_html)
                lbl_w.setTextFormat(Qt.RichText)
                lbl_w.setFixedWidth(82)

                sld = QSlider(Qt.Horizontal); sld.setMinimum(0)
                sld.setMaximum(int(round((mx-mn)/st)))
                sld.setFixedHeight(18)
                sld.setFixedWidth(slider_len)
                sld.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

                s_wrap = QWidget(); swl = QHBoxLayout(s_wrap)
                swl.setContentsMargins(0,0,24,0); swl.setSpacing(0); swl.addWidget(sld)
                s_wrap.setFixedWidth(slider_len + 24)
                s_wrap.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

                sep = QFrame(); sep.setFrameShape(QFrame.VLine); sep.setFrameShadow(QFrame.Plain)
                sep.setLineWidth(1); sep.setStyleSheet("color:#e5e7eb;")

                spn = QDoubleSpinBox()
                spn.setDecimals(dec); spn.setRange(mn, mx); spn.setSingleStep(st); spn.setValue(init)
                spn.setButtonSymbols(QDoubleSpinBox.NoButtons); spn.setFixedWidth(70)

                sld.setValue(int(round((init - mn)/st)))

                cl.addWidget(lbl_w)
                cl.addWidget(s_wrap, 0)
                cl.addWidget(sep)
                cl.addWidget(spn, 0)
                inner.addWidget(cell)
                ctrls.append((key, sld, spn, mn, st))
            return box, ctrls

        size_box, size_ctrls = make_pair(
            "Orbit Size",
            [
                ("a", "a", 0.2, 6.0, 0.01, 1.00, 2),
                ("e", "e",      0.0, 0.95, 0.01, 0.50, 2),
            ],
            slider_len=150
        )
        orient_box, orient_ctrls = make_pair(
            "Orientation",
            [
                ("i", "i (°)", 0.0, 180.0, 1.0, 45.0, 0),
                ("w", "ω (°)", 0.0, 360.0, 1.0, 90.0, 0),
                ("Om","Ω (°)", 0.0, 360.0, 1.0, 90.0, 0),
            ],
            slider_len=150
        )
        masses_box, masses_ctrls = make_pair(
            "Masses",
            [
                ("m1", "m<sub>1</sub>", 0.1, 5.0, 0.1, 1.2, 1),
                ("m2", "m<sub>2</sub>", 0.1, 5.0, 0.1, 0.8, 1),
            ],
            slider_len=150
        )

        params_v.addWidget(size_box)
        params_v.addWidget(orient_box)
        params_v.addWidget(masses_box)

        btns = QWidget(); bl = QHBoxLayout(btns); bl.setContentsMargins(0,0,0,0); bl.setSpacing(8)
        self.btn_play  = QPushButton(" Play");  self.btn_play.setObjectName("primaryBtn")
        self.btn_play.setIcon(QIcon("icons/play.ico"))
        self.btn_reset = QPushButton(" Reset"); self.btn_reset.setObjectName("ghostBtn")
        self.btn_reset.setIcon(QIcon("icons/reset.ico"))
        bl.addWidget(self.btn_play); bl.addWidget(self.btn_reset)

        legend_box = QGroupBox("Legend"); legend_box.setObjectName("legendBox")
        lg = QVBoxLayout(legend_box); lg.setContentsMargins(10,8,10,8); lg.setSpacing(6)
        lg.addWidget(legend_row("Periastron", "periastron"))
        lg.addWidget(legend_row("Ascending node", "asc"))
        lg.addWidget(legend_row("Descending node", "des"))
        lg.addWidget(legend_row("Nodes line", "nodes"))
        lg.addWidget(legend_row("Central star", "star"))
        lg.addWidget(legend_row("Bodies", "bodies"))
        legend_box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        left_v.addWidget(params_group, 2)
        left_v.addWidget(btns, 0)
        left_v.addWidget(legend_box, 1)

        gfx_area = QWidget()
        gfx_v = QVBoxLayout(gfx_area); gfx_v.setContentsMargins(0,0,0,0); gfx_v.setSpacing(8)

        self.tabbar = QTabBar()
        self.tabbar.addTab("Relative Orbit")
        self.tabbar.addTab("Absolute Orbit")
        self.tabbar.setExpanding(False)
        gfx_v.addWidget(self.tabbar, 0)
        self.tabbar.installEventFilter(self)

        gfx_row = QHBoxLayout(); gfx_row.setContentsMargins(0,0,0,0); gfx_row.setSpacing(10)
        gfx_v.addLayout(gfx_row, 1)

        mid_col = QWidget(); mid_v = QVBoxLayout(mid_col); mid_v.setContentsMargins(0,0,0,0); mid_v.setSpacing(0)
        self.stack_3d = QStackedLayout(); mid_v.addLayout(self.stack_3d)

        right_col = QWidget(); right_v = QVBoxLayout(right_col); right_v.setContentsMargins(0,0,0,0); right_v.setSpacing(0)
        self.stack_2d = QStackedLayout(); right_v.addLayout(self.stack_2d)

        gfx_row.addWidget(mid_col, 1)
        gfx_row.addWidget(right_col, 1)

        outer.addWidget(left_col, 1)
        outer.addWidget(gfx_area, 3)

        self.rel_canvas = RelativeCanvas()
        self.abs_canvas = AbsoluteCanvas()

        self.stack_3d.addWidget(self.rel_canvas.card3d)
        self.stack_3d.addWidget(self.abs_canvas.card3d)
        self.stack_2d.addWidget(self.rel_canvas.card2d)
        self.stack_2d.addWidget(self.abs_canvas.card2d)

        self.ctrls = {}
        for key, sld, spn, mn, st in size_ctrls + orient_ctrls + masses_ctrls:
            self.ctrls[key] = (sld, spn, mn, st)

        self._bind("a",  self.on_params_changed_keep_phase)
        self._bind("e",  self.on_e_changed_keep_phase)
        self._bind("i",  self.on_i_changed_keep_phase)
        self._bind("w",  self.on_params_changed_keep_phase)
        self._bind("Om", self.on_params_changed_keep_phase)

        self._bind_mass("m1")
        self._bind_mass("m2")

        self.btn_play.clicked.connect(self.toggle_play)
        self.btn_reset.clicked.connect(self.reset_view)
        self.tabbar.currentChanged.connect(self._on_tab_changed)
        self._on_tab_changed(0)

        self.apply_params_from_init()
        self._sync_left_spacer()

    def show_about(self):
        QMessageBox.about(
            self,
            "About orbel",
            (
                "<b>orbel</b><br><br>"
                "I developed orbel to better understand orbital elements and to visualise relative and absolute Keplerian orbits in 3D and 2D.<br><br>"
                "I started this project during my master's thesis work on astrometry. "
                "At first, it was a simple tool to help me learn orbital dynamics and explain them more clearly to my friends. "
                "Later, I improved it into a complete program.<br><br>"
                "If you have ideas or suggestions for improving orbel, please contact me:<br>"
                '<a href="mailto:efurkanakar@gmail.com">efurkanakar@gmail.com</a><br><br>'
                "© 2025"
            )
        )

    def _bind(self, key, cb):
        sld, spn, mn, st = self.ctrls[key]
        sld.valueChanged.connect(lambda v, mn=mn, st=st, spn=spn: spn.setValue(mn + v*st))
        spn.valueChanged.connect(lambda x, mn=mn, st=st, sld=sld: sld.setValue(int(round((x-mn)/st))))
        spn.valueChanged.connect(cb)

    def _bind_mass(self, key):
        sld, spn, mn, st = self.ctrls[key]
        sld.valueChanged.connect(lambda v, mn=mn, st=st, spn=spn: spn.setValue(mn + v*st))
        spn.valueChanged.connect(lambda x, mn=mn, st=st, sld=sld: sld.setValue(int(round((x-mn)/st))))
        spn.valueChanged.connect(self.on_mass_changed_abs_only)

    def eventFilter(self, obj, event):
        if obj is self.tabbar and event.type() in (QEvent.Resize, QEvent.Show, QEvent.LayoutRequest):
            self._sync_left_spacer()
        return super().eventFilter(obj, event)

    def _sync_left_spacer(self):
        try:
            h = self.tabbar.sizeHint().height()
        except Exception:
            h = 0
        self.left_top_spacer.setFixedHeight(h)

    def _get_params_common(self):
        def val(key): return float(self.ctrls[key][1].value())
        a  = val("a")
        e  = val("e")
        i  = np.deg2rad(val("i"))
        w  = np.deg2rad(val("w"))
        Om = np.deg2rad(val("Om"))
        return a,e,i,w,Om

    def _set_params_common(self, a,e,i,w,Om):
        for key, degval in [("a",a), ("e",e), ("i",np.rad2deg(i)), ("w",np.rad2deg(w)), ("Om",np.rad2deg(Om))]:
            sld, spn, mn, st = self.ctrls[key]
            spn.blockSignals(True); sld.blockSignals(True)
            spn.setValue(degval)
            sld.setValue(int(round((degval - mn)/st)))
            spn.blockSignals(False); sld.blockSignals(False)

    def _get_masses(self):
        def val(key): return float(self.ctrls[key][1].value())
        return val("m1"), val("m2")

    def _set_masses(self, m1, m2):
        for key, v in [("m1", m1), ("m2", m2)]:
            sld, spn, mn, st = self.ctrls[key]
            spn.blockSignals(True); sld.blockSignals(True)
            spn.setValue(v)
            sld.setValue(int(round((v - mn)/st)))
            spn.blockSignals(False); sld.blockSignals(False)

    def _apply_common_to_canvas(self, a,e,i,w,Om):
        for cv in (self.rel_canvas, self.abs_canvas):
            current_nu = getattr(cv, "nu", float(cv.start_nu))
            cv.a, cv.e, cv.i, cv.w, cv.Om = a,e,i,w,Om
            cv._set_nu_keep_phase(current_nu)

        self.rel_canvas._update_axes_limits()
        self.abs_canvas._update_axes_limits()

    def _apply_masses_abs(self, m1, m2):
        self.abs_canvas.m1, self.abs_canvas.m2 = m1, m2

    def apply_params_from_init(self):
        a,e,i,w,Om = (self.rel_canvas.init[k] for k in ["a","e","i","w","Om"])
        m1,m2 = self.rel_canvas.init["m1"], self.rel_canvas.init["m2"]
        start_nu = self.rel_canvas.init["start_nu"]

        self._set_params_common(a,e,i,w,Om)
        self._set_masses(m1,m2)

        for cv in (self.rel_canvas, self.abs_canvas):
            cv.a, cv.e, cv.i, cv.w, cv.Om = a,e,i,w,Om
            cv.m1, cv.m2 = m1, m2
            cv.start_nu = start_nu
            cv._set_nu_keep_phase(start_nu)
            cv.ax3d.view_init(elev=cv.init_elev, azim=cv.init_azim)

        self.rel_canvas.update_all()
        self.abs_canvas.update_all()

    def on_e_changed_keep_phase(self):
        a,e,i,w,Om = self._get_params_common()
        self._apply_common_to_canvas(a,e,i,w,Om)
        self.rel_canvas.update_all(); self.abs_canvas.update_all()

    def on_i_changed_keep_phase(self):
        a,e,i,w,Om = self._get_params_common()
        self._apply_common_to_canvas(a,e,i,w,Om)
        self.rel_canvas.update_all(); self.abs_canvas.update_all()

    def on_params_changed_keep_phase(self):
        a,e,i,w,Om = self._get_params_common()
        self._apply_common_to_canvas(a,e,i,w,Om)
        self.rel_canvas.update_all(); self.abs_canvas.update_all()

    def on_mass_changed_abs_only(self):
        m1,m2 = self._get_masses()
        self._apply_masses_abs(m1,m2)
        self.abs_canvas.update_all()

    def toggle_play(self):
        if self.rel_canvas.timer.isActive() or self.abs_canvas.timer.isActive():
            self.rel_canvas.stop(); self.abs_canvas.stop()
            self.btn_play.setText(" Play");  self.btn_play.setIcon(QIcon("icons/play.ico"))
        else:
            self.rel_canvas.start(); self.abs_canvas.start()
            self.btn_play.setText(" Pause"); self.btn_play.setIcon(QIcon("icons/pause.ico"))

    def reset_view(self):
        self.rel_canvas.stop(); self.abs_canvas.stop()
        self.btn_play.setText(" Play"); self.btn_play.setIcon(QIcon("icons/play.ico"))
        self.apply_params_from_init()

    def _on_tab_changed(self, idx):
        self.stack_3d.setCurrentIndex(idx)
        self.stack_2d.setCurrentIndex(idx)


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    QLocale.setDefault(QLocale(QLocale.English, QLocale.UnitedStates))
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    w = MainWindow(); w.show()
    sys.exit(app.exec_())