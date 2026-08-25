"""
Fenetre 2/3 - LE RAYON
======================
Donnees : ../data/study_radius_increase  (r : 1 -> 1e300, *1.001)
          ../data/study_radius_decrease  (r : 1 -> 1e-300, /1.001)
          (le nom est cherche avec ou sans extension .csv)

On trace uniquement les colonnes du fichier : g en fonction du rayon,
a masse terrestre figee. Six niveaux de zoom sur le meme trace.
Aucune echelle logarithmique, aucune grandeur recalculee.

Usage :  python study_radius.py          (ouvre la fenetre)
         python study_radius.py --save   (ecrit aussi study_radius.png)
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


def readout(ax, x, y, target, label, tpos, ha="left"):
    """Marque la ligne du fichier la plus proche de `target`, avec ses valeurs."""
    i = int(np.argmin(np.abs(x - target)))
    ax.plot(x[i] / ax._xdiv, y[i] / ax._ydiv, "o", ms=7, color=BLUE,
            mec=SURF, mew=2, zorder=4)
    ax.annotate(f"{label}\nr = {x[i]:.6g}\ng = {y[i]:.6g}",
                xy=(x[i] / ax._xdiv, y[i] / ax._ydiv), xytext=tpos,
                fontsize=8.5, color=SEC, linespacing=1.4, ha=ha, va="center",
                arrowprops=dict(arrowstyle="-", color=AXIS, lw=0.9,
                                shrinkA=2, shrinkB=6))


# --------------------------------------------------------------------------
up, dn = load("study_radius_increase"), load("study_radius_decrease")
r_up, g_up = up["radius"], up["gravitational_field"]
r_dn, g_dn = dn["radius"], dn["gravitational_field"]
N_UP, N_DN = len(r_up), len(r_dn)

fig, axes = plt.subplots(2, 3, figsize=(16.5, 9.3))
try:
    fig.canvas.manager.set_window_title("Gravite 2/3 - le rayon")
except Exception:
    pass
fig.suptitle("study_radius_increase / study_radius_decrease   —   g en fonction du rayon, "
             "a masse terrestre figee",
             fontsize=13.5, fontweight="bold", color=INK, x=0.008, ha="left", y=0.985)


def zoom(ax, x, y, xmax, xdiv, ydiv, xunit, yunit, title, total, xmin=0.0):
    sel = (x <= xmax) & (x >= xmin)
    ax.plot(x[sel] / xdiv, y[sel] / ydiv, color=BLUE, zorder=3)
    dress(ax, f"rayon  ({xunit})", f"champ g  ({yunit})")
    ax.set_xlim(xmin / xdiv, xmax / xdiv)
    ax.set_title(title)
    ax.text(0.035, 0.93, f"{nb(int(sel.sum()))} lignes du fichier sur {nb(total)}",
            transform=ax.transAxes, color=MUTED, fontsize=8, va="top")
    ax._xdiv, ax._ydiv = xdiv, ydiv
    return sel


# ==========================================================================
# 1. Tout le fichier croissant, brut
# ==========================================================================
ax = axes[0, 0]
zoom(ax, r_up, g_up, 1e300, 1e299, 1e14, "10²⁹⁹ m", "10¹⁴ m/s²",
     "1. Le fichier croissant en entier", N_UP)
ax.set_ylim(0, 4.4)
n_vis = int((r_up < 1e298).sum())
ax.text(0.97, 0.55, "trace brut : tout est colle a l'axe.\n"
                    f"Les {nb(n_vis)} premieres lignes tiennent\n"
                    "dans le premier centieme de l'axe des x,\n"
                    "et le reste du fichier vaut 0.",
        transform=ax.transAxes, ha="right", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

# ==========================================================================
# 2. Zoom : jusqu'a l'orbite de la Lune
# ==========================================================================
ax = axes[0, 1]
zoom(ax, r_up, g_up, 4e8, 1e6, 1.0, "1000 km", "m/s²",
     "2. Zoom : jusqu'a la distance Terre-Lune", N_UP)
ax.set_ylim(0, 11.5)
readout(ax, r_up, g_up, 6.371e6, "surface de la Terre", (78, 8.7))
readout(ax, r_up, g_up, 3.844e8, "distance de la Lune", (330, 2.6), ha="right")
ax.text(0.97, 0.55, "la gravite ne s'arrete nulle part :\n"
                    "elle decroit et n'atteint jamais zero.\n"
                    "A 384 000 km il reste encore 0,0027 m/s².",
        transform=ax.transAxes, ha="right", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

# ==========================================================================
# 3. Zoom : les orbites
# ==========================================================================
ax = axes[0, 2]
zoom(ax, r_up, g_up, 5e7, 1e6, 1.0, "1000 km", "m/s²",
     "3. Zoom : la zone des satellites", N_UP)
ax.set_ylim(0, 11.5)
readout(ax, r_up, g_up, 6.771e6, "orbite de l'ISS\n(400 km d'altitude)", (12.5, 8.0))
readout(ax, r_up, g_up, 2.657e7, "orbite GPS", (29, 4.2))
readout(ax, r_up, g_up, 4.216e7, "orbite geostationnaire", (49, 1.4), ha="right")
ax.text(0.97, 0.60, "entre la surface et le geostationnaire,\n"
                    "g est divise par 44 en 35 000 km.",
        transform=ax.transAxes, ha="right", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

# ==========================================================================
# 4. Le fichier decroissant : la ou g explose
# ==========================================================================
ax = axes[1, 0]
sel = (r_dn <= 2e-146) & (r_dn > 0)
ax.plot(r_dn[sel] / 1e-147, np.where(np.isinf(g_dn[sel]), np.nan, g_dn[sel]) / 1e307,
        color=BLUE, zorder=3)
dress(ax, "rayon  (10⁻¹⁴⁷ m)", "champ g  (10³⁰⁷ m/s²)")
first_inf = int(np.argmax(np.isinf(g_dn)))
ax.axvline(r_dn[first_inf] / 1e-147, color=RED, lw=1.4, ls=(0, (4, 3)), zorder=2)
ax.set_xlim(0, 20)
ax.set_ylim(0, 20)
ax.set_title("4. Le fichier decroissant : g monte sans limite")
n_inf = int(np.isinf(g_dn).sum())
ax.text(0.035, 0.93, f"{nb(int(sel.sum()))} lignes du fichier sur {nb(N_DN)}",
        transform=ax.transAxes, color=MUTED, fontsize=8, va="top")
ax.annotate(f"a partir de r = {r_dn[first_inf]:.6g} m\n"
            f"le fichier contient inf\n({nb(n_inf)} lignes)",
            xy=(r_dn[first_inf] / 1e-147, 12), xytext=(5.6, 14.5),
            fontsize=8.5, color=RED, linespacing=1.4,
            arrowprops=dict(arrowstyle="->", color=RED, lw=1.2))
ax.text(0.97, 0.30, "plus on comprime la Terre, plus g grimpe.\n"
                    "Ici on est deja a 10³⁰⁷ m/s² : la courbe\n"
                    "monte a la verticale et sort du type double.",
        transform=ax.transAxes, ha="right", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

# ==========================================================================
# 5. La fin du fichier croissant
# ==========================================================================
ax = axes[1, 1]
sel = (r_up >= 1.15e154) & (r_up <= 1.55e154)
ax.plot(r_up[sel] / 1e154, g_up[sel] / 1e-294, color=BLUE, zorder=3)
dress(ax, "rayon  (10¹⁵⁴ m)", "champ g  (10⁻²⁹⁴ m/s²)")
first_zero = int(np.argmax(g_up == 0.0))
ax.axvline(r_up[first_zero] / 1e154, color=RED, lw=1.4, ls=(0, (4, 3)), zorder=2)
ax.set_xlim(1.15, 1.55)
ax.set_ylim(0, 3.4)
ax.set_title("5. La fin du fichier croissant : g tombe a 0 d'un coup")
n_zero = int((g_up == 0.0).sum())
ax.text(0.035, 0.93, f"{nb(int(sel.sum()))} lignes du fichier sur {nb(N_UP)}",
        transform=ax.transAxes, color=MUTED, fontsize=8, va="top")
ax.annotate(f"a partir de r = {r_up[first_zero]:.6g} m\n"
            f"le fichier ne contient plus que des 0\n({nb(n_zero)} lignes)",
            xy=(r_up[first_zero] / 1e154, 1.1), xytext=(1.185, 1.75),
            fontsize=8.5, color=RED, linespacing=1.4,
            arrowprops=dict(arrowstyle="->", color=RED, lw=1.2))
ax.text(0.97, 0.06, "la courbe ne s'aplatit pas doucement :\n"
                    "elle passe de 2,2·10⁻²⁹⁴ a 0 en une ligne.",
        transform=ax.transAxes, ha="right", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

# ==========================================================================
# 6. Extrait du fichier
# ==========================================================================
ax = axes[1, 2]
ax.axis("off")
ax.set_title("6. Ce qu'il y a dans le fichier, a quelques endroits")
lines = ["radius             gravitational_field", ""]
for target, tag in [(1.0, "1re ligne"), (6.371e6, "rayon terrestre"),
                    (4.216e7, "geostationnaire"), (3.844e8, "distance Lune"),
                    (1.496e11, "distance Soleil")]:
    i = int(np.argmin(np.abs(r_up - target)))
    lines.append(f"{r_up[i]:<18.6g} {g_up[i]:<14.6g} {tag}")
i = first_zero
lines.append(f"{r_up[i]:<18.6g} {g_up[i]:<14.6g} premier 0")
i = first_inf
lines.append(f"{r_dn[i]:<18.6g} {str(g_dn[i]):<14} premier inf")
ax.text(0.0, 0.86, "\n".join(lines), transform=ax.transAxes, fontsize=9,
        family="monospace", color=INK, va="top", linespacing=1.75)
ax.text(0.0, 0.13, f"{nb(N_UP)} lignes dans study_radius_increase\n"
                   f"{nb(N_DN)} lignes dans study_radius_decrease",
        transform=ax.transAxes, fontsize=8.5, color=SEC, va="top", linespacing=1.6)

fig.tight_layout(rect=(0, 0, 1, 0.955))
if "--save" in sys.argv:
    fig.savefig(os.path.join(HERE, "study_radius.png"), dpi=130, facecolor=SURF)
    print("study_radius.png ecrit")
plt.show()