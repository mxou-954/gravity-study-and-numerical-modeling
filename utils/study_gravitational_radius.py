"""
Fenetre 3/3 - LE RAYON D'INFLUENCE
==================================
Donnees : ../data/study_gravitational_radius  (M : 1e-3 -> 1e300, *1.001)
          (le nom est cherche avec ou sans extension .csv)

On trace uniquement les colonnes du fichier : la distance a laquelle le champ
tombe sous le seuil minimum_gravity, en fonction de la masse.
Six niveaux de zoom sur le meme trace, aucune echelle logarithmique.

Usage :  python study_gravitational_radius.py          (ouvre la fenetre)
         python study_gravitational_radius.py --save   (ecrit aussi le PNG)
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


# --------------------------------------------------------------------------
d = load("study_gravitational_radius")
M, RG = d["celestial_body_mass"], d["gravitational_radius"]
GMIN = float(d["minimum_gravity"][0])
N = len(M)

fig, axes = plt.subplots(2, 3, figsize=(16.5, 9.3))
try:
    fig.canvas.manager.set_window_title("Gravite 3/3 - le rayon d'influence")
except Exception:
    pass
fig.suptitle(f"study_gravitational_radius   —   distance a laquelle g tombe sous "
             f"{GMIN:g} m/s², en fonction de la masse",
             fontsize=13.5, fontweight="bold", color=INK, x=0.008, ha="left", y=0.985)


def zoom(ax, mmax, xdiv, ydiv, xunit, yunit, title):
    sel = M <= mmax
    ax.plot(M[sel] / xdiv, RG[sel] / ydiv, color=BLUE, zorder=3)
    dress(ax, f"masse du corps  ({xunit})", f"rayon d'influence  ({yunit})")
    ax.set_xlim(0, mmax / xdiv)
    ax.set_title(title)
    ax.text(0.035, 0.93, f"{nb(int(sel.sum()))} lignes du fichier sur {nb(N)}",
            transform=ax.transAxes, color=MUTED, fontsize=8, va="top")
    ax._xdiv, ax._ydiv = xdiv, ydiv
    return sel


def readout(ax, target, label, tpos, ha="left"):
    i = int(np.argmin(np.abs(M - target)))
    ax.plot(M[i] / ax._xdiv, RG[i] / ax._ydiv, "o", ms=7, color=BLUE,
            mec=SURF, mew=2, zorder=4)
    ax.annotate(f"{label}\nM = {M[i]:.6g}\nr = {RG[i]:.6g}",
                xy=(M[i] / ax._xdiv, RG[i] / ax._ydiv), xytext=tpos,
                fontsize=8.5, color=SEC, linespacing=1.4, ha=ha, va="center",
                arrowprops=dict(arrowstyle="-", color=AXIS, lw=0.9,
                                shrinkA=2, shrinkB=6))


# ==========================================================================
# 1. Tout le fichier
# ==========================================================================
ax = axes[0, 0]
zoom(ax, 1e300, 1e299, 1e145, "10²⁹⁹ kg", "10¹⁴⁵ m",
     "1. Le fichier en entier")
ax.set_ylim(0, 28)
ax.text(0.97, 0.06, "une racine carree : la courbe monte vite\n"
                    "au debut puis s'aplatit. C'est la seule des\n"
                    "trois etudes ou le trace brut montre deja\n"
                    "quelque chose.",
        transform=ax.transAxes, ha="right", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

# ==========================================================================
# 2. Zoom : masses planetaires
# ==========================================================================
ax = axes[0, 1]
zoom(ax, 7e24, 1e24, 1e6, "10²⁴ kg", "1000 km",
     "2. Zoom : l'echelle des planetes")
ax.set_ylim(0, 760)
readout(ax, 5.972e24, "≈ masse de la Terre", (3.3, 570))
readout(ax, 6.417e23, "≈ masse de Mars", (2.1, 165))
ax.text(0.97, 0.06, "pour la Terre, le seuil est atteint a\n"
                    "631 000 km — soit 1,6 fois plus loin\n"
                    "que la Lune.",
        transform=ax.transAxes, ha="right", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

# ==========================================================================
# 3. Zoom : un asteroide / une montagne
# ==========================================================================
ax = axes[0, 2]
zoom(ax, 1e12, 1e9, 1.0, "10⁹ kg", "m",
     "3. Zoom : l'echelle d'un gros rocher")
ax.set_ylim(0, 290)
readout(ax, 1e12, "1 milliard de tonnes", (760, 150), ha="right")
ax.text(0.97, 0.06, "meme forme, autre echelle : un corps de\n"
                    "10¹² kg se fait sentir jusqu'a 258 m.",
        transform=ax.transAxes, ha="right", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

# ==========================================================================
# 4. Zoom : l'echelle humaine
# ==========================================================================
ax = axes[1, 0]
zoom(ax, 100.0, 1.0, 1e-3, "kg", "mm",
     "4. Zoom : l'echelle du quotidien")
ax.set_ylim(0, 2.9)
readout(ax, 70.0, "70 kg", (52, 1.55), ha="right")
readout(ax, 1.0, "1 kg", (18, 0.55))
ax.text(0.97, 0.06, "un corps de 70 kg impose encore\n"
                    f"{GMIN:g} m/s² a 2 mm de son centre.",
        transform=ax.transAxes, ha="right", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

# ==========================================================================
# 5. Le debut du fichier
# ==========================================================================
ax = axes[1, 1]
zoom(ax, 1.0, 1e-3, 1e-6, "grammes", "µm",
     "5. Zoom : les toutes premieres lignes du fichier")
ax.set_ylim(0, 290)
readout(ax, 1e-3, "1re ligne du fichier", (330, 60))
readout(ax, 1.0, "1 kg", (760, 190), ha="right")
ax.text(0.97, 0.06, "la courbe part de 8 µm et pas de zero :\n"
                    "le fichier commence a 1 gramme, pas a 0.",
        transform=ax.transAxes, ha="right", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

# ==========================================================================
# 6. Extrait du fichier
# ==========================================================================
ax = axes[1, 2]
ax.axis("off")
ax.set_title("6. Ce qu'il y a dans le fichier, a quelques endroits")
lines = ["celestial_body_mass   gravitational_radius", ""]
for target, tag in [(1e-3, "1re ligne"), (1.0, "1 kg"), (70.0, "70 kg"),
                    (1e12, "10⁹ tonnes"), (7.342e22, "≈ Lune"),
                    (5.972e24, "≈ Terre"), (1.989e30, "≈ Soleil"),
                    (1e300, "derniere ligne")]:
    i = int(np.argmin(np.abs(M - target)))
    lines.append(f"{M[i]:<21.6g} {RG[i]:<14.6g} {tag}")
ax.text(0.0, 0.86, "\n".join(lines), transform=ax.transAxes, fontsize=9,
        family="monospace", color=INK, va="top", linespacing=1.75)
bad = int((RG == 0).sum() + (~np.isfinite(RG)).sum())
ax.text(0.0, 0.10, f"{nb(N)} lignes, seuil minimum_gravity = {GMIN:g} m/s²\n"
                   + (f"{nb(bad)} valeurs nulles ou infinies" if bad else
                      "aucune valeur nulle ni infinie dans ce fichier"),
        transform=ax.transAxes, fontsize=8.5, color=SEC, va="top", linespacing=1.6)

fig.tight_layout(rect=(0, 0, 1, 0.955))
if "--save" in sys.argv:
    fig.savefig(os.path.join(HERE, "study_gravitational_radius.png"), dpi=130,
                facecolor=SURF)
    print("study_gravitational_radius.png ecrit")
plt.show()