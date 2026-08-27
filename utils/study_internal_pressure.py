"""
Fenetre 8 - LA PRESSION INTERNE
===============================
Donnees : ../data/study_internal_pressure_without_compression
          colonnes : density, radius, dP/dr, delta_r, delta_P, pressure
          (le nom est cherche avec ou sans extension .csv)

Contrairement aux autres etudes, celle-ci accumule : chaque ligne ajoute sa
contribution a la colonne `pressure`. Les quatre colonnes intermediaires sont
donc tracees separement, dans l'ordre ou elles interviennent :

    dP/dr  ->  delta_r  ->  delta_P  ->  pressure

Les axes sont lineaires et les echelles choisies pour que chaque colonne soit
lisible telle qu'elle est ecrite dans le fichier.

Usage :  python study_internal_pressure.py          (ouvre la fenetre)
         python study_internal_pressure.py --save   (ecrit aussi le PNG)
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


def span(v, frac=0.10):
    """Bornes d'axe generees a partir des donnees, zero toujours inclus."""
    lo, hi = float(np.nanmin(v)), float(np.nanmax(v))
    lo, hi = min(lo, 0.0), max(hi, 0.0)
    pad = frac * (hi - lo or abs(hi) or 1.0)
    return lo - pad, hi + pad


def curve(ax, x, y, xlabel, ylabel, title, lines_note=True):
    ax.plot(x, y, color=BLUE, zorder=3)
    dress(ax, xlabel, ylabel)
    ax.set_title(title)
    ax.set_xlim(0, x.max() * 1.06)
    ax.set_ylim(*span(y))
    if 0 >= ax.get_ylim()[0] and 0 <= ax.get_ylim()[1]:
        ax.axhline(0, color=AXIS, lw=1, zorder=2)
    if lines_note:
        ax.text(0.035, 0.94, f"{nb(len(x))} lignes — tout le fichier",
                transform=ax.transAxes, color=MUTED, fontsize=8, va="top")
    return ax


def mark(ax, x, y, i, label, tpos, ha="left", unit=""):
    ax.plot(x[i], y[i], "o", ms=7, color=BLUE, mec=SURF, mew=2, zorder=5)
    ax.annotate(f"{label}\n{y[i]:.6g}{unit}", xy=(x[i], y[i]), xytext=tpos,
                fontsize=8.5, color=SEC, linespacing=1.4, ha=ha, va="center",
                arrowprops=dict(arrowstyle="-", color=AXIS, lw=0.9,
                                shrinkA=2, shrinkB=6))


# --------------------------------------------------------------------------
D = load("study_internal_pressure_without_compression")
r = D["radius"]
dpdr = D["dP/dr"]
dr = D["delta_r"]
dP = D["delta_P"]
P = D["pressure"]
RHO = float(D["density"][0])
N = len(r)
R_SURF = float(r.max())
depth = R_SURF - r                      # meme colonne, vue depuis la surface
GPA = 1e9

fig, axes = plt.subplots(2, 3, figsize=(16.5, 9.3))
try:
    fig.canvas.manager.set_window_title("Gravite 8 - la pression interne")
except Exception:
    pass
fig.suptitle(f"study_internal_pressure_without_compression   —   densite figee a "
             f"{RHO:g} kg/m³, du rayon terrestre jusqu'au centre",
             fontsize=13.5, fontweight="bold", color=INK, x=0.008, ha="left", y=0.985)

# ==========================================================================
# 1. dP/dr
# ==========================================================================
ax = axes[0, 0]
curve(ax, r / 1e6, dpdr / 1e3, "rayon  (1000 km)", "dP/dr  (kPa par metre)",
      "1. dP/dr, colonne 3")
mark(ax, r / 1e6, dpdr / 1e3, 0, "au rayon terrestre", (3.5, dpdr[0] / 1e3 * 0.78),
     unit=" kPa/m")
ax.text(0.97, 0.06, "le gradient de pression suit le champ interieur :\n"
                    "proportionnel a la distance au centre, nul au centre.",
        transform=ax.transAxes, ha="right", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

# ==========================================================================
# 2. delta_r
# ==========================================================================
ax = axes[0, 1]
curve(ax, r / 1e6, dr / 1e3, "rayon  (1000 km)", "delta_r  (km)",
      "2. delta_r, le pas de la boucle")
i_big = int(np.argmax(np.abs(dr)))
mark(ax, r / 1e6, dr / 1e3, i_big, "pas le plus large",
     (3.6, dr[i_big] / 1e3 * 0.62), unit=" km")
ax.text(0.035, 0.06, "le pas vaut 0,1 % du rayon courant : il retrecit\n"
                     "en meme temps que la boucle descend, jusqu'a\n"
                     "des pas de l'ordre du micrometre pres du centre.",
        transform=ax.transAxes, ha="left", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

# ==========================================================================
# 3. delta_P
# ==========================================================================
ax = axes[0, 2]
curve(ax, r / 1e6, dP / 1e6, "rayon  (1000 km)", "delta_P  (MPa)",
      "3. delta_P, la contribution de chaque ligne")
i_dp = int(np.argmax(np.abs(dP)))
mark(ax, r / 1e6, dP / 1e6, i_dp, "contribution la plus forte",
     (3.55, dP[i_dp] / 1e6 * 0.60), unit=" MPa")
ax.text(0.035, 0.06, "produit des deux colonnes precedentes : maximal\n"
                     "juste sous la surface, ou le gradient et le pas\n"
                     "sont tous les deux au plus grand.",
        transform=ax.transAxes, ha="left", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

# ==========================================================================
# 4. pressure en fonction du rayon
# ==========================================================================
ax = axes[1, 0]
curve(ax, r / 1e6, P / GPA, "rayon  (1000 km)", "pressure  (GPa)",
      "4. pressure, la somme accumulee")
mark(ax, r / 1e6, P / GPA, int(np.argmin(r)), "derniere ligne",
     (2.3, P[-1] / GPA * 0.62), unit=" GPa")
ax.text(0.97, 0.06, "la somme demarre a 0 au rayon terrestre et\n"
                    "s'accumule ligne apres ligne jusqu'au centre.",
        transform=ax.transAxes, ha="right", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

# ==========================================================================
# 5. la meme colonne, vue en profondeur
# ==========================================================================
ax = axes[1, 1]
curve(ax, depth / 1e3, P / GPA, "profondeur sous la surface  (km)",
      "pressure  (GPa)", "5. La meme colonne, lue en profondeur", lines_note=False)
ax.set_xlim(0, 6500)
for prof, label, tpos, ha in [(1e5, "100 km", (900, P[np.argmin(np.abs(depth - 1e5))] / GPA - 12), "left"),
                              (6.6e5, "660 km", (1650, P[np.argmin(np.abs(depth - 6.6e5))] / GPA - 16), "left"),
                              (2.89e6, "2 890 km", (3550, P[np.argmin(np.abs(depth - 2.89e6))] / GPA + 22), "left")]:
    i = int(np.argmin(np.abs(depth - prof)))
    mark(ax, depth / 1e3, P / GPA, i, label, tpos, ha=ha, unit=" GPa")
ax.text(0.035, 0.06, "profondeur = rayon terrestre − rayon : c'est la meme\n"
                     "colonne, lue dans l'autre sens.",
        transform=ax.transAxes, color=SEC, fontsize=8, linespacing=1.5,
        va="bottom")

# ==========================================================================
# 6. Extrait du fichier
# ==========================================================================
ax = axes[1, 2]
ax.axis("off")
ax.set_title("6. Ce qu'il y a dans le fichier")
rows = ["radius        dP/dr       delta_r      delta_P      pressure", ""]
picks = [(0, "1re ligne"), (1, "2e ligne"),
         (int(np.argmin(np.abs(r - 3.48e6))), "mi-rayon"),
         (int(np.argmin(np.abs(r - 1.22e6))), "1 220 km"),
         (int(np.argmin(np.abs(r - 1e3))), "1 km"),
         (N - 1, "derniere ligne")]
for i, tag in picks:
    rows.append(f"{r[i]:<13.6g} {dpdr[i]:<11.6g} {dr[i]:<12.6g} "
                f"{dP[i]:<12.6g} {P[i]:<12.6g} {tag}")
ax.text(0.0, 0.96, "\n".join(rows), transform=ax.transAxes, fontsize=7.6,
        family="monospace", color=INK, va="top", linespacing=1.8)
ax.text(0.0, 0.52,
        f"{nb(N)} lignes, du rayon terrestre a 1 mm du centre.\n\n"
        f"pressure va de {P[0] / GPA:.6g} GPa a {P[-1] / GPA:.6g} GPa.\n"
        f"dP/dr va de {dpdr[0]:.6g} a {dpdr[-1]:.3g} Pa/m.\n"
        f"delta_r va de {dr[0]:.6g} a {dr[-1]:.3g} m.\n\n"
        "Aucune valeur nulle ni infinie hors la premiere\n"
        "ligne : la plage est trop courte pour inquieter\n"
        "un double."
        if not (np.isinf(P).any() or np.isnan(P).any()) else
        f"{nb(N)} lignes.\nAttention : la colonne pressure contient des\n"
        "valeurs non finies.",
        transform=ax.transAxes, fontsize=8.5, color=SEC, va="top", linespacing=1.6)

fig.tight_layout(rect=(0, 0, 1, 0.955))
if "--save" in sys.argv:
    fig.savefig(os.path.join(HERE, "study_internal_pressure.png"), dpi=130,
                facecolor=SURF)
    print("study_internal_pressure.png ecrit")
plt.show()