"""
Fenetre 1/3 - LA MASSE
======================
Donnees : ../data/study_mass_increase  (M : 1 -> 1e300, *1.001)
          ../data/study_mass_decrease  (M : 1 -> 1e-300, /1.001)
          (le nom est cherche avec ou sans extension .csv)

On trace uniquement les colonnes du fichier : g en fonction de la masse.
Comme le fichier couvre 600 decades, une seule fenetre ne peut pas tout
montrer : les 6 panneaux sont le meme trace, a 6 niveaux de zoom.
Aucune echelle logarithmique, aucune grandeur recalculee.

Usage :  python study_mass.py          (ouvre la fenetre)
         python study_mass.py --save   (ecrit aussi study_mass.png)
"""

import os
import sys

import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------------------------------------
# Style
# --------------------------------------------------------------------------
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
up, dn = load("study_mass_increase"), load("study_mass_decrease")
m_up, g_up = up["celestial_body_mass"], up["gravitational_field"]
m_dn, g_dn = dn["celestial_body_mass"], dn["gravitational_field"]
N_UP, N_DN = len(m_up), len(m_dn)

fig, axes = plt.subplots(2, 3, figsize=(16.5, 9.3))
try:
    fig.canvas.manager.set_window_title("Gravite 1/3 - la masse")
except Exception:
    pass
fig.suptitle("study_mass_increase / study_mass_decrease   —   g en fonction de la masse, "
             "a rayon terrestre fige",
             fontsize=13.5, fontweight="bold", color=INK, x=0.008, ha="left", y=0.985)


def zoom(ax, m, g, mmax, xdiv, ydiv, xunit, yunit, title, total):
    """Trace g en fonction de m sur [0, mmax], en unites lisibles."""
    sel = m <= mmax
    ax.plot(m[sel] / xdiv, g[sel] / ydiv, color=BLUE, zorder=3)
    dress(ax, f"masse du corps  ({xunit})", f"champ g  ({yunit})")
    ax.set_xlim(0, mmax / xdiv)
    ax.set_title(title)
    ax.text(0.035, 0.93, f"{nb(int(sel.sum()))} lignes du fichier sur {nb(total)}",
            transform=ax.transAxes, color=MUTED, fontsize=8, va="top")
    return sel


def readout(ax, m, g, target, label, tpos, ha="left"):
    """Marque la ligne du fichier la plus proche de `target` et affiche ses valeurs."""
    i = int(np.argmin(np.abs(m - target)))
    ax.plot(m[i] / ax._xdiv, g[i] / ax._ydiv, "o", ms=7, color=BLUE,
            mec=SURF, mew=2, zorder=4)
    ax.annotate(f"{label}\nM = {m[i]:.6g}\ng = {g[i]:.6g}",
                xy=(m[i] / ax._xdiv, g[i] / ax._ydiv), xytext=tpos,
                fontsize=8.5, color=SEC, linespacing=1.4, ha=ha, va="center",
                arrowprops=dict(arrowstyle="-", color=AXIS, lw=0.9,
                                shrinkA=2, shrinkB=6))


# ==========================================================================
# 1. Tout le fichier croissant, brut
# ==========================================================================
ax = axes[0, 0]
ax._xdiv, ax._ydiv = 1e299, 1e275
zoom(ax, m_up, g_up, 1e300, 1e299, 1e275, "10²⁹⁹ kg", "10²⁷⁵ m/s²",
     "1. Le fichier croissant en entier", N_UP)
ax.set_ylim(0, 17.5)
pct = 100.0 * (m_up < 1e298).sum() / N_UP
ax.text(0.97, 0.06, "une droite : g suit la masse exactement.\n"
                    f"Mais {pct:.1f} % des lignes tiennent dans le\n"
                    "premier centieme de l'axe — d'ou les zooms\n"
                    "des panneaux suivants.",
        transform=ax.transAxes, ha="right", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

# ==========================================================================
# 2. Zoom : masses planetaires
# ==========================================================================
ax = axes[0, 1]
ax._xdiv, ax._ydiv = 1e24, 1.0
zoom(ax, m_up, g_up, 8e24, 1e24, 1.0, "10²⁴ kg", "m/s²",
     "2. Zoom : l'echelle des planetes", N_UP)
ax.set_ylim(0, 16.5)
readout(ax, m_up, g_up, 5.972e24, "≈ masse de la Terre", (3.2, 13.6))
readout(ax, m_up, g_up, 6.417e23, "≈ masse de Mars", (2.6, 4.2))
ax.text(0.97, 0.06, "meme droite, autre echelle : le zoom\n"
                    "ne change rien a sa forme.",
        transform=ax.transAxes, ha="right", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

# ==========================================================================
# 3. Zoom : echelle humaine
# ==========================================================================
ax = axes[0, 2]
ax._xdiv, ax._ydiv = 1.0, 1e-22
zoom(ax, m_up, g_up, 100.0, 1.0, 1e-22, "kg", "10⁻²² m/s²",
     "3. Zoom : l'echelle du quotidien", N_UP)
ax.set_ylim(0, 1.9)
readout(ax, m_up, g_up, 1.0, "1re ligne du fichier", (17, 0.28))
readout(ax, m_up, g_up, 70.0, "70 kg", (55, 1.52), ha="right")
ax.text(0.97, 0.06, "encore la meme droite. La gravite n'a pas\n"
                    "de seuil : 1 kg produit un champ, juste\n"
                    "tres petit.",
        transform=ax.transAxes, ha="right", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

# ==========================================================================
# 4. Tout le fichier decroissant
# ==========================================================================
ax = axes[1, 0]
ax._xdiv, ax._ydiv = 1.0, 1e-24
zoom(ax, m_dn, g_dn, 1.0, 1.0, 1e-24, "kg", "10⁻²⁴ m/s²",
     "4. Le fichier decroissant en entier", N_DN)
ax.set_ylim(0, 1.9)
ax.text(0.06, 0.82, "de 1 kg a 10⁻³⁰⁰ kg :\n"
                    "la droite continue, et tout le fichier\n"
                    "s'ecrase sur le coin bas-gauche.",
        transform=ax.transAxes, color=SEC, fontsize=8, linespacing=1.5, va="top")

# ==========================================================================
# 5. La fin du fichier decroissant
# ==========================================================================
ax = axes[1, 1]
sel = m_dn <= 8e-300
ax.step(m_dn[sel] / 1e-300, g_dn[sel] / 1e-323, where="post", color=BLUE, zorder=3)
dress(ax, "masse du corps  (10⁻³⁰⁰ kg)", "champ g  (10⁻³²³ m/s²)")
ax.set_xlim(0.9, 8.2)
ax.set_ylim(0, 1.55)
ax.set_title("5. Zoom : la toute fin du fichier decroissant")
n_zero = int((g_dn == 0.0).sum())
ax.text(0.035, 0.93, f"{nb(int(sel.sum()))} lignes du fichier sur {nb(N_DN)}",
        transform=ax.transAxes, color=MUTED, fontsize=8, va="top")
ax.text(0.34, 0.50, "ici la courbe devient un escalier :\n"
                    "la masse continue de descendre ligne\n"
                    "apres ligne, mais la valeur de g ne\n"
                    f"change plus, puis reste a 0 sur les\n{nb(n_zero)} dernieres lignes.",
        transform=ax.transAxes, color=SEC, fontsize=8, linespacing=1.5, va="top")

# ==========================================================================
# 6. Extrait du fichier
# ==========================================================================
ax = axes[1, 2]
ax.axis("off")
ax.set_title("6. Ce qu'il y a dans le fichier, a quelques endroits")
lines = ["celestial_body_mass       gravitational_field", ""]
for target, tag in [(1e300, "fin du croissant"), (5.972e24, "≈ Terre"),
                    (1e12, ""), (1.0, "1re ligne")]:
    i = int(np.argmin(np.abs(m_up - target)))
    lines.append(f"{m_up[i]:<14.6g} {g_up[i]:<18.6g} {tag}")
for target, tag in [(1e-12, ""), (1.3e-284, "1er sous-normal"),
                    (1.5e-300, "premier 0"), (1e-300, "fin du decroissant")]:
    i = int(np.argmin(np.abs(m_dn - target)))
    lines.append(f"{m_dn[i]:<14.6g} {g_dn[i]:<18.6g} {tag}")
ax.text(0.0, 0.86, "\n".join(lines), transform=ax.transAxes, fontsize=9,
        family="monospace", color=INK, va="top", linespacing=1.75)
ax.text(0.0, 0.10, f"{nb(N_UP)} lignes dans study_mass_increase\n"
                   f"{nb(N_DN)} lignes dans study_mass_decrease",
        transform=ax.transAxes, fontsize=8.5, color=SEC, va="top", linespacing=1.6)

fig.tight_layout(rect=(0, 0, 1, 0.955))
if "--save" in sys.argv:
    fig.savefig(os.path.join(HERE, "study_mass.png"), dpi=130, facecolor=SURF)
    print("study_mass.png ecrit")
plt.show()