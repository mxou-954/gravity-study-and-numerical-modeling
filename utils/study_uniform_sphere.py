"""
Fenetre 6 - LA SPHERE UNIFORME
==============================
Donnees : ../data/study_density_effect_on_gravity
          ../data/study_radius_effect_on_surface_gravity_constant_density
          ../data/study_density_effect_on_surface_gravity_constant_mass
          (les noms sont cherches avec ou sans extension .csv)

Les trois etudes utilisent gravitational_field_outside_uniform_sphere, mais ne
font varier ni la meme chose ni a masse constante :

  1. densite variable, rayon fige au rayon terrestre       -> exposant attendu  +1
  2. rayon variable, densite figee a la densite terrestre  -> exposant attendu  +1
  3. densite variable, MASSE figee (le rayon suit)         -> exposant attendu  +2/3

Ligne du haut : les colonnes du CSV en axes lineaires, sur une plage lisible.
Ligne du bas  : les memes colonnes en log10-log10, avec la pente mesuree.

Usage :  python study_uniform_sphere.py          (ouvre la fenetre)
         python study_uniform_sphere.py --save   (ecrit aussi le PNG)
"""

import os
import sys

import numpy as np
import matplotlib.pyplot as plt

BLUE, ORANGE, AQUA, YELLOW, VIOLET, RED = (
    "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#4a3aa7", "#e34948")
INK, SEC, MUTED, GRID, AXIS, SURF = (
    "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb")

plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "font.size": 9,
    "axes.edgecolor": AXIS, "axes.labelcolor": SEC, "axes.titlecolor": INK,
    "axes.titlesize": 10, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "axes.titlepad": 8, "axes.labelsize": 8.5,
    "xtick.color": MUTED, "ytick.color": MUTED, "xtick.labelsize": 8,
    "ytick.labelsize": 8, "grid.color": GRID, "grid.linewidth": 0.8,
    "lines.linewidth": 2, "legend.frameon": False, "legend.fontsize": 8,
})

DBL_MAX = 1.7976931348623157e308


def dress(ax, xlabel="", ylabel=""):
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_linewidth(0.9)
    ax.grid(axis="y", alpha=1.0)
    ax.set_axisbelow(True)
    return ax


HERE = os.path.dirname(os.path.abspath(__file__))


def find(name):
    roots = [os.path.join(HERE, "..", "data"), os.path.join(HERE, "data"),
             os.path.join(os.getcwd(), "..", "data"),
             os.path.join(os.getcwd(), "data")]
    tried = []
    for root in roots:
        for cand in (name + ".csv", name, name + ".txt"):
            path = os.path.normpath(os.path.join(root, cand))
            tried.append(path)
            if os.path.isfile(path):
                return path
    sys.exit("Fichier de donnees introuvable. Chemins essayes :\n  "
             + "\n  ".join(dict.fromkeys(tried)))


def load(name):
    path = find(name)
    try:
        import pandas as pd
        df = pd.read_csv(path)
        return {c: df[c].to_numpy(dtype=float) for c in df.columns}
    except ImportError:
        with open(path) as f:
            cols = f.readline().strip().split(",")
        arr = np.loadtxt(path, delimiter=",", skiprows=1)
        return {c: arr[:, i] for i, c in enumerate(cols)}


def nb(n):
    return f"{n:,}".replace(",", " ")


def loglog_fit(x, y):
    ok = np.isfinite(x) & np.isfinite(y) & (x > 0) & (y > 0)
    lx, ly = np.log10(x[ok]), np.log10(y[ok])
    slope, intercept = np.polyfit(lx, ly, 1)
    resid = ly - (slope * lx + intercept)
    return dict(lx=lx, ly=ly, slope=float(slope), intercept=float(intercept),
                worst=float(np.abs(resid).max()), n=int(ok.sum()), total=len(x),
                x=x, y=y)


# --------------------------------------------------------------------------
D1 = load("study_density_effect_on_gravity")
D2 = load("study_radius_effect_on_surface_gravity_constant_density")
D3 = load("study_density_effect_on_surface_gravity_constant_mass")

f1 = loglog_fit(D1["density"], D1["gravitational_field"])
f2 = loglog_fit(D2["radius"], D2["gravitational_field"])
f3 = loglog_fit(D3["density"], D3["gravitational_field"])

R_FIX = float(D1["radius"][0])          # rayon fige de l'etude 1
RHO_FIX = float(D2["density"][0])       # densite figee de l'etude 2
M_FIX = float(D3["earth_mass"][0]) if "earth_mass" in D3 else float("nan")

fig, axes = plt.subplots(2, 3, figsize=(16.5, 9.3))
try:
    fig.canvas.manager.set_window_title("Gravite 6 - la sphere uniforme")
except Exception:
    pass
fig.suptitle("gravitational_field_outside_uniform_sphere   —   trois facons de faire "
             "varier la meme formule",
             fontsize=13.5, fontweight="bold", color=INK, x=0.008, ha="left", y=0.985)


def linear_panel(ax, x, y, xmax, xdiv, ydiv, xunit, yunit, title, total, ymax):
    sel = (x > 0) & (x <= xmax) & np.isfinite(y)
    ax.plot(x[sel] / xdiv, y[sel] / ydiv, color=BLUE, zorder=3)
    dress(ax, xunit, yunit)
    ax.set_xlim(0, xmax / xdiv)
    ax.set_ylim(0, ymax)
    ax.set_title(title)
    ax.text(0.035, 0.93, f"{nb(int(sel.sum()))} lignes du fichier sur {nb(total)}",
            transform=ax.transAxes, color=MUTED, fontsize=8, va="top")
    ax._xdiv, ax._ydiv = xdiv, ydiv


def readout(ax, x, y, target, label, tpos, ha="left"):
    i = int(np.argmin(np.abs(x - target)))
    ax.plot(x[i] / ax._xdiv, y[i] / ax._ydiv, "o", ms=7, color=BLUE,
            mec=SURF, mew=2, zorder=4)
    ax.annotate(f"{label}\n{y[i]:.4g} m/s²",
                xy=(x[i] / ax._xdiv, y[i] / ax._ydiv), xytext=tpos,
                fontsize=8.5, color=SEC, linespacing=1.4, ha=ha, va="center",
                arrowprops=dict(arrowstyle="-", color=AXIS, lw=0.9,
                                shrinkA=2, shrinkB=6))


def loglog_panel(ax, f, xlabel, title, expected, expected_txt, note):
    st = max(1, f["n"] // 4000)
    ax.plot(f["lx"][::st], f["ly"][::st], color=BLUE, lw=3.2, zorder=3,
            label="donnees du CSV")
    xs = np.array([f["lx"].min(), f["lx"].max()])
    ax.plot(xs, f["slope"] * xs + f["intercept"], color=ORANGE, lw=1.3,
            ls=(0, (5, 4)), zorder=4, label="droite ajustee")
    dress(ax, xlabel, "log10(g)  [g en m/s²]")
    ax.set_title(title)
    ax.legend(loc="upper left")
    ax.text(0.97, 0.52,
            f"pente mesuree  =  {f['slope']:.10f}\n"
            f"pente attendue =  {expected_txt}\n"
            f"ecart           =  {abs(f['slope'] - expected):.1e}\n"
            f"{nb(f['n'])} lignes exploitables\n"
            f"{nb(f['total'] - f['n'])} lignes ecartees (inf ou 0)",
            transform=ax.transAxes, fontsize=8.5, family="monospace", ha="right",
            color=INK, va="top", linespacing=1.7)
    ax.text(0.97, 0.02, note, transform=ax.transAxes, fontsize=8, color=SEC,
            ha="right", va="bottom", linespacing=1.5)


def lost_decades(f):
    """Jusqu'ou la loi mesuree resterait representable en double, compare a
    l'endroit ou le fichier bascule reellement a inf."""
    bad = ~np.isfinite(f["y"]) | (f["y"] == 0)
    if not bad.any():
        return None
    x_break = float(f["x"][int(np.argmax(bad))])
    # exposant (base 10) de la valeur ou la loi mesuree atteindrait DBL_MAX
    e_limit = (np.log10(DBL_MAX) - f["intercept"]) / f["slope"]
    return x_break, float(e_limit), float(e_limit - np.log10(x_break))


# ==========================================================================
# Ligne du haut : les colonnes brutes, en lineaire
# ==========================================================================
ax = axes[0, 0]
linear_panel(ax, D1["density"], D1["gravitational_field"], 22000.0, 1.0, 1.0,
             "densite du corps  (kg/m³)", "g a la surface  (m/s²)",
             "1. Densite variable, rayon terrestre fige", f1["total"], 46)
readout(ax, D1["density"], D1["gravitational_field"], 1000, "densite de l'eau", (3400, 6.5))
readout(ax, D1["density"], D1["gravitational_field"], RHO_FIX,
        "densite moyenne\nde la Terre", (9000, 16.5))
readout(ax, D1["density"], D1["gravitational_field"], 19300, "densite de l'or",
        (18000, 40.5), ha="right")
ax.text(0.97, 0.06, f"rayon fige a {R_FIX:.6g} m.\n"
                    "g est proportionnel a la densite :\n"
                    "doubler la densite double g.",
        transform=ax.transAxes, ha="right", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

ax = axes[0, 1]
linear_panel(ax, D2["radius"], D2["gravitational_field"], 8e6, 1e6, 1.0,
             "rayon du corps  (1000 km)", "g a la surface  (m/s²)",
             "2. Rayon variable, densite terrestre figee", f2["total"], 13)
readout(ax, D2["radius"], D2["gravitational_field"], 1.7374e6,
        "rayon de la Lune", (2.55, 3.6))
readout(ax, D2["radius"], D2["gravitational_field"], 6.371e6,
        "rayon de la Terre", (4.1, 10.9))
ax.text(0.97, 0.06, f"densite figee a {RHO_FIX:g} kg/m³.\n"
                    "A densite egale, g est proportionnel au\n"
                    "rayon : un corps deux fois plus gros a\n"
                    "deux fois plus de gravite en surface.",
        transform=ax.transAxes, ha="right", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

ax = axes[0, 2]
linear_panel(ax, D3["density"], D3["gravitational_field"], 22000.0, 1.0, 1.0,
             "densite imposee  (kg/m³)", "g a la surface  (m/s²)",
             "3. Densite variable, masse terrestre figee", f3["total"], 30)
readout(ax, D3["density"], D3["gravitational_field"], 1000, "densite de l'eau", (3600, 5.2))
readout(ax, D3["density"], D3["gravitational_field"], RHO_FIX,
        "densite reelle\nde la Terre", (9600, 15.5))
readout(ax, D3["density"], D3["gravitational_field"], 19300,
        "compressee a la\ndensite de l'or", (17800, 26.5), ha="right")
ax.text(0.97, 0.06, "ici la masse ne change pas : comprimer la\n"
                    "Terre reduit son rayon, et g augmente —\n"
                    "mais moins vite que la densite.",
        transform=ax.transAxes, ha="right", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

# ==========================================================================
# Ligne du bas : les memes colonnes en log10-log10
# ==========================================================================
l1 = lost_decades(f1)
loglog_panel(axes[1, 0], f1, "log10(densite)",
             "4. Etude 1 en log10–log10", 1.0, "1.0000000000",
             f"le fichier bascule a inf des {l1[0]:.3g} kg/m³ ;\n"
             f"la loi mesuree tiendrait jusqu'a 10^{l1[1]:.0f},\n"
             f"soit {l1[2]:.0f} decades perdues par depassement\n"
             "de la masse intermediaire." if l1 else "aucune ligne ecartee.")

l2 = lost_decades(f2)
loglog_panel(axes[1, 1], f2, "log10(rayon)",
             "5. Etude 2 en log10–log10", 1.0, "1.0000000000",
             f"le fichier bascule a inf des {l2[0]:.3g} m ;\n"
             f"la loi mesuree tiendrait jusqu'a 10^{l2[1]:.0f},\n"
             f"soit {l2[2]:.0f} decades perdues par depassement\n"
             "de la masse intermediaire." if l2 else "aucune ligne ecartee.")

loglog_panel(axes[1, 2], f3, "log10(densite)",
             "6. Etude 3 en log10–log10", 2.0 / 3.0, "0.6666666667",
             "2/3 et pas 1 : a masse figee, augmenter la\n"
             "densite fait aussi retrecir le rayon, et les\n"
             "deux effets se combinent. Aucune ligne\n"
             "ecartee dans ce fichier.")

fig.tight_layout(rect=(0, 0, 1, 0.955))
if "--save" in sys.argv:
    fig.savefig(os.path.join(HERE, "study_uniform_sphere.png"), dpi=130, facecolor=SURF)
    print("study_uniform_sphere.png ecrit")
plt.show()