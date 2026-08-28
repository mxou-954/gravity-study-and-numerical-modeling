"""
Fenetre 11 - PRESSION INTERNE AVEC COMPRESSION (PREM)
=====================================================
Donnees : ../data/study_internal_pressure_with_compression_layer_by_layer_PREM
          17 colonnes : radius, density, delta_mass, outside_mass, enclosed_mass,
          gravitational_field, dP/dr, delta_r, delta_P, pressure, pressure_before,
          pressure_shell, V_old, total_volume, delta_V, V_new, new_density
          (le nom du fichier est cherche avec ou sans extension .csv)

Les dix premieres colonnes sont deja couvertes par la fenetre PREM sans
compression ; celle-ci se concentre sur les sept colonnes ajoutees par le
calcul de compression : les volumes et la densite recalculee.

Les unites des axes sont choisies a partir des donnees, et le zoom des
panneaux 2 et 7 est cale sur la plus grande interface detectee dans la
colonne density. Rien n'est code en dur : si la boucle C++ change de bornes,
les axes suivent.

Usage :  python study_pressure_compression.py          (ouvre la fenetre)
         python study_pressure_compression.py --save   (ecrit aussi le PNG)
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
    "lines.linewidth": 1.8, "legend.frameon": False, "legend.fontsize": 8,
})

SUP = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


def sup(e):
    return str(int(e)).translate(SUP)


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
    """Ignore les noms de colonnes vides de l'en-tete (virgule finale) et
    aligne les colonnes sur la FIN des lignes de donnees."""
    path = find(name)
    with open(path) as f:
        cols = [c.strip() for c in f.readline().strip().split(",") if c.strip()]
    try:
        import pandas as pd
        raw = pd.read_csv(path, header=None, skiprows=1).to_numpy(dtype=float)
    except ImportError:
        raw = np.genfromtxt(path, delimiter=",", skip_header=1)
    off = raw.shape[1] - len(cols)
    if off < 0:
        sys.exit(f"{path} : {raw.shape[1]} champs pour {len(cols)} colonnes nommees.")
    return {c: raw[:, off + k] for k, c in enumerate(cols)}, cols


def nb(n):
    return f"{n:,}".replace(",", " ")


def unit(v):
    """Choisit un diviseur puissance de 10 et le suffixe d'unite qui va avec."""
    m = np.nanmax(np.abs(v[np.isfinite(v)])) if np.isfinite(v).any() else 0.0
    if m == 0:
        return 1.0, ""
    e = int(np.floor(np.log10(m)))
    if -2 <= e <= 3:
        return 1.0, ""
    return 10.0 ** e, f"10{sup(e)} "


def span(*arrays, frac=0.10):
    vals = np.concatenate([a[np.isfinite(a)] for a in arrays])
    lo, hi = float(vals.min()), float(vals.max())
    lo, hi = min(lo, 0.0), max(hi, 0.0)
    pad = frac * (hi - lo or abs(hi) or 1.0)
    return lo - pad, hi + pad


# --------------------------------------------------------------------------
D, COLS = load("study_internal_pressure_with_compression_layer_by_layer_PREM")
r = D["radius"]
N = len(r)
R_MAX = float(np.nanmax(r))
def radius_unit(rmax):
    if rmax <= 2e7:
        return 1e6, "1000 km"
    d, suf = unit(np.array([rmax]))
    return d, suf + "m"


RDIV, RSUF = radius_unit(R_MAX)
RLAB = f"rayon  ({RSUF})"
NOTE = f"{nb(N)} lignes — tout le fichier"

rho = D["density"]
THRESH = 0.008 * (np.nanmax(rho) - np.nanmin(rho))
idx = np.nonzero(np.abs(np.diff(rho)) > THRESH)[0]
IFACES = [float(r[k + 1]) for k in idx]
R_ZOOM = min(R_MAX, 1.15 * max(IFACES)) if IFACES else R_MAX
ZOOMED = R_ZOOM < 0.8 * R_MAX
Z = r <= R_ZOOM
ZDIV, ZSUF = radius_unit(R_ZOOM)          # le zoom a sa propre unite
ZLAB = f"rayon  ({ZSUF})"

fig, axes = plt.subplots(2, 4, figsize=(19.5, 9.3))
try:
    fig.canvas.manager.set_window_title("Gravite 11 - compression, PREM")
except Exception:
    pass
fig.suptitle("study_internal_pressure_with_compression_layer_by_layer_PREM   —   "
             "les colonnes ajoutees par la compression",
             fontsize=13.5, fontweight="bold", color=INK, x=0.007, ha="left", y=0.985)


def base(ax, title, xmax, ylabel, note=True, rdiv=None, rlab=None):
    dress(ax, rlab or RLAB, ylabel)
    ax.set_title(title)
    ax.set_xlim(0, xmax / (rdiv or RDIV) * 1.04)
    if note:
        ax.text(0.035, 0.94, NOTE, transform=ax.transAxes, color=MUTED,
                fontsize=8, va="top")


def series(ax, ys, labels, colors, sel=None, legend="best", rdiv=None,
           widths=None):
    m = np.ones(N, bool) if sel is None else sel
    div, suf = unit(np.concatenate([y[m] for y in ys]))
    rd = rdiv or RDIV
    for k, (y, lab, col) in enumerate(zip(ys, labels, colors)):
        lw = widths[k] if widths else 1.8
        ax.plot(r[m] / rd, y[m] / div, color=col, label=lab, lw=lw, zorder=3 + k)
    ax.set_ylim(*span(*[y[m] / div for y in ys]))
    lo, hi = ax.get_ylim()
    if lo <= 0 <= hi:
        ax.axhline(0, color=AXIS, lw=1, zorder=2)
    if len(ys) > 1:
        ax.legend(loc=legend)
    return suf


def ifaces(ax, rdiv=None):
    for rr in IFACES:
        ax.axvline(rr / (rdiv or RDIV), color=AXIS, lw=1.0, ls=(0, (3, 4)),
                   zorder=2)


# ==========================================================================
# 1-2. density et new_density
# ==========================================================================
ax = axes[0, 0]
suf = series(ax, [D["density"], D["new_density"]], ["density", "new_density"],
             [BLUE, ORANGE])
base(ax, "1. density et new_density", R_MAX, f"masse volumique  ({suf}kg/m³)")

ax = axes[0, 1]
suf = series(ax, [D["density"], D["new_density"]], ["density", "new_density"],
             [BLUE, ORANGE], sel=Z, rdiv=ZDIV)
base(ax, "2. Zoom : " + (f"r ≤ {R_ZOOM / 1e3:,.0f} km".replace(",", " ")
                         if ZOOMED else "meme plage"), R_ZOOM,
     f"masse volumique  ({suf}kg/m³)", note=False, rdiv=ZDIV, rlab=ZLAB)
ifaces(ax, ZDIV)
ax.text(0.035, 0.94, f"{nb(int(Z.sum()))} lignes sur {nb(N)}",
        transform=ax.transAxes, color=MUTED, fontsize=8, va="top")

# ==========================================================================
# 3. V_old et V_new
# ==========================================================================
ax = axes[0, 2]
suf = series(ax, [D["V_old"], D["V_new"]], ["V_old", "V_new"], [BLUE, ORANGE])
base(ax, "3. V_old et V_new", R_MAX, f"volume de la coquille  ({suf}m³)")

# ==========================================================================
# 4. delta_V
# ==========================================================================
ax = axes[0, 3]
suf = series(ax, [D["delta_V"]], ["delta_V"], [BLUE])
base(ax, "4. delta_V", R_MAX, f"delta_V  ({suf}m³)")

# ==========================================================================
# 5. total_volume
# ==========================================================================
ax = axes[1, 0]
suf = series(ax, [D["total_volume"]], ["total_volume"], [BLUE])
base(ax, "5. total_volume, cumule", R_MAX, f"total_volume  ({suf}m³)")

# ==========================================================================
# 6. les trois colonnes de pression
# ==========================================================================
ax = axes[1, 1]
suf = series(ax, [D["pressure"], D["pressure_before"], D["pressure_shell"]],
             ["pressure", "pressure_before", "pressure_shell"],
             [BLUE, ORANGE, AQUA], legend="upper right",
             widths=[3.6, 2.1, 1.0])
base(ax, "6. pressure, pressure_before, pressure_shell", R_MAX,
     f"pression  ({suf}Pa)")

# ==========================================================================
# 7. pression, zoom
# ==========================================================================
ax = axes[1, 2]
suf = series(ax, [D["pressure"]], ["pressure"], [BLUE], sel=Z, rdiv=ZDIV)
base(ax, "7. Zoom : " + (f"pressure sur r ≤ {R_ZOOM / 1e3:,.0f} km".replace(",", " ")
                         if ZOOMED else "pressure, meme plage"),
     R_ZOOM, f"pressure  ({suf}Pa)", note=False, rdiv=ZDIV, rlab=ZLAB)
ifaces(ax, ZDIV)
ax.text(0.035, 0.94, f"{nb(int(Z.sum()))} lignes sur {nb(N)}",
        transform=ax.transAxes, color=MUTED, fontsize=8, va="top")

# ==========================================================================
# 8. min / max de chaque colonne
# ==========================================================================
ax = axes[1, 3]
ax.axis("off")
ax.set_title("8. Chaque colonne, du min au max")
rows = [f"{'colonne':<20}{'min':>12} {'max':>12}", ""]
bad_total = 0
for c in COLS:
    v = D[c]
    fin = np.isfinite(v)
    bad = int((~fin).sum())
    bad_total += bad
    if fin.any():
        rows.append(f"{c:<20}{np.min(v[fin]):>12.4g} {np.max(v[fin]):>12.4g}"
                    + (f"  {bad} non fini" if bad else ""))
    else:
        rows.append(f"{c:<20}{'—':>12} {'—':>12}  {bad} non fini")
ax.text(0.0, 0.99, "\n".join(rows), transform=ax.transAxes, fontsize=6.7,
        family="monospace", color=INK, va="top", linespacing=1.62)
ax.text(0.0, 0.09,
        f"{nb(N)} lignes  ·  {len(COLS)} colonnes nommees\n"
        + (f"{bad_total} valeur(s) non finie(s) au total"
           if bad_total else "aucune valeur non finie")
        + f"\n{len(IFACES)} interfaces detectees dans density",
        transform=ax.transAxes, fontsize=8.5, color=SEC, va="top", linespacing=1.6)

fig.tight_layout(rect=(0, 0, 1, 0.955))
if "--save" in sys.argv:
    fig.savefig(os.path.join(HERE, "study_pressure_compression.png"), dpi=125,
                facecolor=SURF)
    print("study_pressure_compression.png ecrit")
plt.show()