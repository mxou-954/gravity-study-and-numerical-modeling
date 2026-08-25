"""
Fenetre 4/4 - RAYON, MASSE ET DENSITE
=====================================
Donnees : ../data/study_constant_density_incremented_radius  (radius, density, mass)
          ../data/study_constant_mass_incremented_radius     (radius, mass, density)
          (le nom est cherche avec ou sans extension .csv)

Les deux fichiers parcourent le meme rayon (0,001 m -> 1e300, *1.001).
  - le premier fige la densite terrestre et lit la masse obtenue
  - le second fige la masse terrestre et lit la densite necessaire
Ligne du haut = premier fichier, ligne du bas = second.
On trace uniquement les colonnes des fichiers, a plusieurs niveaux de zoom.
Aucune echelle logarithmique, aucune grandeur recalculee.

Usage :  python study_density.py          (ouvre la fenetre)
         python study_density.py --save   (ecrit aussi study_density.png)
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


SUP = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


def sup(e):
    return str(int(e)).translate(SUP)


def first_index(mask):
    """Indice du 1er True, ou -1 s'il n'y en a aucun."""
    return int(np.argmax(mask)) if bool(mask.any()) else -1


def decade(v):
    """Puissance de 10 juste en dessous de v (pour choisir l'unite de l'axe)."""
    return 10.0 ** np.floor(np.log10(abs(v)))


def window(ax, x, y, xmin, xmax, xdiv, ydiv, xunit, yunit, title, total):
    """Trace y en fonction de x sur [xmin, xmax], en unites lisibles."""
    sel = (x >= xmin) & (x <= xmax)
    ax.plot(x[sel] / xdiv, np.where(np.isfinite(y[sel]), y[sel], np.nan) / ydiv,
            color=BLUE, zorder=3)
    dress(ax, f"rayon  ({xunit})", yunit)
    ax.set_xlim(xmin / xdiv, xmax / xdiv)
    ax.set_title(title)
    ax.text(0.035, 0.93, f"{nb(int(sel.sum()))} lignes du fichier sur {nb(total)}",
            transform=ax.transAxes, color=MUTED, fontsize=8, va="top")
    ax._xdiv, ax._ydiv = xdiv, ydiv
    return sel


def readout(ax, x, y, target, label, ylabel_name, tpos, ha="left"):
    i = int(np.argmin(np.abs(x - target)))
    ax.plot(x[i] / ax._xdiv, y[i] / ax._ydiv, "o", ms=7, color=BLUE,
            mec=SURF, mew=2, zorder=4)
    ax.annotate(f"{label}\nrayon = {x[i]:.6g}\n{ylabel_name} = {y[i]:.6g}",
                xy=(x[i] / ax._xdiv, y[i] / ax._ydiv), xytext=tpos,
                fontsize=8.5, color=SEC, linespacing=1.4, ha=ha, va="center",
                arrowprops=dict(arrowstyle="-", color=AXIS, lw=0.9,
                                shrinkA=2, shrinkB=6))


def table(ax, title, header, rows, footer):
    ax.axis("off")
    ax.set_title(title)
    ax.text(0.0, 0.90, "\n".join([header, ""] + rows), transform=ax.transAxes,
            fontsize=8.5, family="monospace", color=INK, va="top", linespacing=1.8)
    ax.text(0.0, 0.16, footer, transform=ax.transAxes, fontsize=8.5, color=SEC,
            va="top", linespacing=1.6)


# --------------------------------------------------------------------------
A = load("study_constant_density_incremented_radius")
B = load("study_constant_mass_incremented_radius")
rA, dens_fixed, mass = A["radius"], A["density"], A["mass"]
rB, mass_fixed, dens = B["radius"], B["mass"], B["density"]
NA, NB = len(rA), len(rB)
RHO, MFIX = float(dens_fixed[0]), float(mass_fixed[0])

first_inf = first_index(~np.isfinite(mass))
n_inf = int((~np.isfinite(mass)).sum())
first_zero = first_index(dens == 0.0)
n_zero = int((dens == 0.0).sum())

fig, axes = plt.subplots(2, 4, figsize=(19.5, 9.3))
try:
    fig.canvas.manager.set_window_title("Gravite 4/4 - rayon, masse et densite")
except Exception:
    pass
fig.suptitle("study_constant_density_incremented_radius (haut)   /   "
             "study_constant_mass_incremented_radius (bas)",
             fontsize=13.5, fontweight="bold", color=INK, x=0.007, ha="left", y=0.985)

# ==========================================================================
# HAUT : densite figee, on lit la masse
# ==========================================================================
ax = axes[0, 0]
window(ax, rA, mass, 0.0, 2.0, 1.0, 1e3, "m", "masse  (tonnes)",
       "1. Densite figee : zoom sur 2 metres", NA)
ax.set_ylim(0, 200)
readout(ax, rA, mass, 1.0, "sphere de 1 m de rayon", "masse", (0.42, 130))
ax.text(0.97, 0.06, f"densite figee a {RHO:g} kg/m³.\n"
                    "La masse suit le cube du rayon :\n"
                    "doubler le rayon multiplie par 8.",
        transform=ax.transAxes, ha="right", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

ax = axes[0, 1]
window(ax, rA, mass, 0.0, 8e6, 1e6, 1e24, "1000 km", "masse  (10²⁴ kg)",
       "2. Densite figee : zoom sur l'echelle planetaire", NA)
ax.set_ylim(0, 12)
readout(ax, rA, mass, 6.371e6, "au rayon terrestre", "masse", (2.2, 8.4))
ax.text(0.97, 0.06, "a 6 371 km on retrouve la masse de la\n"
                    "Terre : les deux etudes precedentes et\n"
                    "celle-ci sont bien coherentes.",
        transform=ax.transAxes, ha="right", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

ax = axes[0, 2]
if first_inf > 0:
    rc, mc = rA[first_inf], mass[first_inf - 1]
    xd, yd = decade(rc), decade(mc)
    window(ax, rA, mass, rc / 1.55, rc * 1.18, xd, yd, f"10{sup(np.log10(xd))} m",
           f"masse  (10{sup(np.log10(yd))} kg)",
           "3. Densite figee : la fin de la partie finie", NA)
    ax.axvline(rc / xd, color=RED, lw=1.4, ls=(0, (4, 3)), zorder=2)
    ax.set_ylim(0, 1.4 * (mc / yd))
    ax.annotate(f"a partir de r = {rc:.6g} m\nla colonne mass vaut inf\n"
                f"({nb(n_inf)} lignes, soit {100 * n_inf / NA:.0f} % du fichier)",
                xy=(rc / xd, 0.87 * (mc / yd)), xytext=(rc * 1.16 / xd, 0.48 * (mc / yd)),
                ha="right", fontsize=8.5, color=RED, linespacing=1.4,
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.2))
else:
    ax.axis("off")
    ax.set_title("3. Densite figee : aucune valeur infinie dans ce fichier")
ax.text(0.03, 0.05, "le cube du rayon depasse le plus grand\n"
                    "double bien avant la fin de la boucle.",
        transform=ax.transAxes, ha="left", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

rows = []
for target, tag in [(1e-3, "1re ligne"), (1.0, "1 m"), (1e3, "1 km"),
                    (6.371e6, "rayon terrestre"), (6.96e8, "rayon du Soleil")]:
    i = int(np.argmin(np.abs(rA - target)))
    rows.append(f"{rA[i]:<14.6g} {mass[i]:<14.6g} {tag}")
if first_inf > 0:
    rows.append(f"{rA[first_inf]:<14.6g} {'inf':<14} premier inf")
table(axes[0, 3], "4. Ce qu'il y a dans le fichier",
      "radius         mass", rows,
      f"{nb(NA)} lignes\ndensity constante = {RHO:g} kg/m³\n"
      f"{nb(n_inf)} lignes a inf")

# ==========================================================================
# BAS : masse figee, on lit la densite
# ==========================================================================
ax = axes[1, 0]
window(ax, rB, dens, 0.5, 3.0, 1.0, 1e24, "m", "densite  (10²⁴ kg/m³)",
       "5. Masse figee : zoom sur 3 metres", NB)
ax.set_ylim(0, 14.5)
readout(ax, rB, dens, 1.0, "toute la Terre dans\nune sphere de 1 m", "densite",
        (1.60, 8.4))
ax.text(0.97, 0.06, f"masse figee a {MFIX:g} kg.\n"
                    "La densite suit l'inverse du cube :\n"
                    "diviser le rayon par 2 multiplie par 8.",
        transform=ax.transAxes, ha="right", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

ax = axes[1, 1]
window(ax, rB, dens, 4e6, 1.5e7, 1e6, 1e3, "1000 km", "densite  (1000 kg/m³)",
       "6. Masse figee : zoom sur l'echelle planetaire", NB)
ax.set_ylim(0, 26)
readout(ax, rB, dens, 6.371e6, "au rayon terrestre", "densite", (9.2, 17.5))
ax.text(0.97, 0.06, "a 6 371 km on retrouve la densite\n"
                    "moyenne de la Terre, celle qui est figee\n"
                    "dans l'autre fichier.",
        transform=ax.transAxes, ha="right", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

ax = axes[1, 2]
if first_zero > 0:
    rc, dc = rB[first_zero], dens[first_zero - 1]
    xd, yd = decade(rc), decade(dc)
    window(ax, rB, dens, rc / 1.35, rc * 1.25, xd, yd, f"10{sup(np.log10(xd))} m",
           f"densite  (10{sup(np.log10(yd))} kg/m³)",
           "7. Masse figee : la fin des valeurs non nulles", NB)
    ax.axvline(rc / xd, color=RED, lw=1.4, ls=(0, (4, 3)), zorder=2)
    ax.set_ylim(0, 2.9 * (dc / yd))
    ax.annotate(f"a partir de r = {rc:.6g} m\nla colonne density vaut 0\n"
                f"({nb(n_zero)} lignes, soit {100 * n_zero / NB:.0f} % du fichier)",
                xy=(rc / xd, 1.05 * (dc / yd)), xytext=(rc * 1.24 / xd, 2.1 * (dc / yd)),
                ha="right", fontsize=8.5, color=RED, linespacing=1.4,
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.2))
else:
    ax.axis("off")
    ax.set_title("7. Masse figee : aucune valeur nulle dans ce fichier")
ax.text(0.97, 0.06, "meme cause que ci-dessus : c'est le cube\n"
                    "du rayon qui deborde, et la division\n"
                    "renvoie 0 au lieu d'une valeur non nulle.",
        transform=ax.transAxes, ha="right", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

rows = []
for target, tag in [(1e-3, "1re ligne"), (1.0, "1 m"), (1e3, "1 km"),
                    (6.371e6, "rayon terrestre"), (6.96e8, "rayon du Soleil")]:
    i = int(np.argmin(np.abs(rB - target)))
    rows.append(f"{rB[i]:<14.6g} {dens[i]:<14.6g} {tag}")
if first_zero > 0:
    rows.append(f"{rB[first_zero]:<14.6g} {dens[first_zero]:<14.6g} premier 0")
table(axes[1, 3], "8. Ce qu'il y a dans le fichier",
      "radius         density", rows,
      f"{nb(NB)} lignes\nmass constante = {MFIX:g} kg\n"
      f"{nb(n_zero)} lignes a 0")

fig.tight_layout(rect=(0, 0, 1, 0.955))
if "--save" in sys.argv:
    fig.savefig(os.path.join(HERE, "study_density.png"), dpi=125, facecolor=SURF)
    print("study_density.png ecrit")
plt.show()