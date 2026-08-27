"""
Fenetre 10 - PRESSION INTERNE, PROFIL PREM
==========================================
Donnees : ../data/study_internal_pressure_without_compression_layer_by_layer_PREM
          colonnes : radius, density, delta_mass, outside_mass, enclosed_mass,
                     gravitational_field, dP/dr, delta_r, delta_P, pressure
          (le nom est cherche avec ou sans extension .csv)

Meme structure que l'etude a deux couches, mais la densite vient de
define_density() et le pas est dix fois plus fin. Les dix colonnes sont
tracees dans l'ordre du calcul.

Les interfaces (sauts de la colonne density) sont detectees dans les donnees
et reportees en pointilles sur tous les panneaux, pour que les colonnes se
lisent les unes en regard des autres.

Usage :  python study_pressure_prem.py          (ouvre la fenetre)
         python study_pressure_prem.py --save   (ecrit aussi le PNG)
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
    """Aligne les colonnes sur la FIN de ligne : tolere un champ en trop
    au debut des lignes de donnees."""
    path = find(name)
    with open(path) as f:
        cols = f.readline().strip().split(",")
    try:
        import pandas as pd
        raw = pd.read_csv(path, header=None, skiprows=1).to_numpy(dtype=float)
    except ImportError:
        raw = np.genfromtxt(path, delimiter=",", skip_header=1)
    off = raw.shape[1] - len(cols)
    if off < 0:
        sys.exit(f"{path} : {raw.shape[1]} champs pour {len(cols)} colonnes.")
    return {c: raw[:, off + k] for k, c in enumerate(cols)}


def nb(n):
    return f"{n:,}".replace(",", " ")


def span(v, frac=0.10):
    lo, hi = float(np.nanmin(v)), float(np.nanmax(v))
    lo, hi = min(lo, 0.0), max(hi, 0.0)
    pad = frac * (hi - lo or abs(hi) or 1.0)
    return lo - pad, hi + pad


# --------------------------------------------------------------------------
D = load("study_internal_pressure_without_compression_layer_by_layer_PREM")
r = D["radius"]
rho = D["density"]
dm = D["delta_mass"]
m_out = D["outside_mass"]
m_in = D["enclosed_mass"]
g = D["gravitational_field"]
dpdr = D["dP/dr"]
dr = D["delta_r"]
dP = D["delta_P"]
P = D["pressure"]
N = len(r)
R_SURF = float(r.max())
GPA = 1e9
NOTE = f"{nb(N)} lignes — tout le fichier"

# interfaces : sauts de la colonne density, lus dans les donnees
THRESH = 0.008 * (np.nanmax(rho) - np.nanmin(rho))
idx = np.nonzero(np.abs(np.diff(rho)) > THRESH)[0]
IFACES = [(float(r[k + 1]), float(rho[k]), float(rho[k + 1])) for k in idx]
# les deux sauts de densite les plus marques, pour l'etiquetage
BIG = sorted(IFACES, key=lambda t: -abs(t[2] - t[1]))[:2]

fig, axes = plt.subplots(2, 4, figsize=(19.5, 9.3))
try:
    fig.canvas.manager.set_window_title("Gravite 10 - pression interne, PREM")
except Exception:
    pass
fig.suptitle("study_internal_pressure_without_compression_layer_by_layer_PREM   —   "
             "les dix colonnes, dans l'ordre du calcul",
             fontsize=13.5, fontweight="bold", color=INK, x=0.007, ha="left", y=0.985)


def ifaces(ax):
    for rr, _, _ in IFACES:
        ax.axvline(rr / 1e6, color=AXIS, lw=1.0, ls=(0, (3, 4)), zorder=2)


def curve(ax, y, ylabel, title, note=True):
    ax.plot(r / 1e6, y, color=BLUE, lw=1.8, zorder=3)
    dress(ax, "rayon  (1000 km)", ylabel)
    ax.set_title(title)
    ax.set_xlim(0, R_SURF / 1e6 * 1.06)
    ax.set_ylim(*span(y))
    lo, hi = ax.get_ylim()
    if lo <= 0 <= hi:
        ax.axhline(0, color=AXIS, lw=1, zorder=2)
    ifaces(ax)
    if note:
        ax.text(0.035, 0.94, NOTE, transform=ax.transAxes, color=MUTED,
                fontsize=8, va="top")
    return ax


def mark(ax, y, i, label, tpos, ha="left", unit="", fmt="{:.6g}"):
    ax.plot(r[i] / 1e6, y[i], "o", ms=7, color=BLUE, mec=SURF, mew=2, zorder=5)
    ax.annotate(f"{label}\n{fmt.format(y[i])}{unit}", xy=(r[i] / 1e6, y[i]),
                xytext=tpos, fontsize=8.5, color=SEC, linespacing=1.4,
                ha=ha, va="center",
                arrowprops=dict(arrowstyle="-", color=AXIS, lw=0.9,
                                shrinkA=2, shrinkB=6))


# ==========================================================================
# 1. density
# ==========================================================================
ax = axes[0, 0]
curve(ax, rho, "density  (kg/m³)", "1. density : le profil du fichier")
for k, (rr, a, b) in enumerate(BIG):
    ax.annotate(f"r = {rr / 1e3:,.0f} km".replace(",", " ") +
                f"\n{a:.0f} → {b:.0f} kg/m³",
                xy=(rr / 1e6, (a + b) / 2), xytext=(0.30, rho.max() * (0.30 - 0.15 * k)),
                fontsize=8.5, color=SEC, linespacing=1.4, ha="left",
                arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.1))
ax.text(0.97, 0.06, f"{len(IFACES)} sauts detectes dans la colonne\n"
                    "density ; tous sont reportes en pointilles\n"
                    "sur les huit panneaux.",
        transform=ax.transAxes, ha="right", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

# ==========================================================================
# 2. delta_mass
# ==========================================================================
ax = axes[0, 1]
curve(ax, dm / 1e18, "delta_mass  (10¹⁸ kg)",
      "2. delta_mass : la masse de chaque coquille")
i_dm = int(np.argmax(dm))
mark(ax, dm / 1e18, i_dm, "coquille la plus lourde",
     (2.9, dm[i_dm] / 1e18 * 0.72), unit=" ×10¹⁸ kg")

# ==========================================================================
# 3. enclosed_mass et outside_mass
# ==========================================================================
ax = axes[0, 2]
ax.plot(r / 1e6, m_in / 1e24, color=BLUE, lw=1.8, zorder=3, label="enclosed_mass")
ax.plot(r / 1e6, m_out / 1e24, color=ORANGE, lw=1.8, zorder=3, label="outside_mass")
dress(ax, "rayon  (1000 km)", "masse  (10²⁴ kg)")
ax.set_title("3. enclosed_mass et outside_mass")
ax.set_xlim(0, R_SURF / 1e6 * 1.06)
ax.set_ylim(*span(np.concatenate([m_in, m_out]) / 1e24))
ifaces(ax)
ax.legend(loc="center left")
ax.text(0.035, 0.94, NOTE, transform=ax.transAxes, color=MUTED, fontsize=8, va="top")
ax.text(0.06, 0.30, f"les deux se somment a\n{(m_in[0] + m_out[0]) / 1e24:.6g}·10²⁴ kg\n"
                    "sur chaque ligne.",
        transform=ax.transAxes, ha="left", color=SEC, fontsize=8,
        linespacing=1.5, va="top")

# ==========================================================================
# 4. gravitational_field
# ==========================================================================
ax = axes[0, 3]
curve(ax, g, "gravitational_field  (m/s²)", "4. gravitational_field")
i_max = int(np.argmax(g))
mark(ax, g, i_max, "maximum de la colonne", (3.9, g.max() * 0.72), unit=" m/s²")
mark(ax, g, 0, "1re ligne", (5.25, g.max() * 0.58), unit=" m/s²")
ax.text(0.035, 0.06, f"le maximum n'est pas a la 1re ligne :\n"
                     f"il tombe a r = {r[i_max] / 1e3:,.0f} km".replace(",", " ") + ".",
        transform=ax.transAxes, ha="left", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

# ==========================================================================
# 5. dP/dr
# ==========================================================================
ax = axes[1, 0]
curve(ax, dpdr / 1e3, "dP/dr  (kPa par metre)", "5. dP/dr")
i_dp = int(np.argmin(dpdr))
mark(ax, dpdr / 1e3, i_dp, "extremum de la colonne",
     (3.6, dpdr.min() / 1e3 * 0.42), unit=" kPa/m")

# ==========================================================================
# 6. delta_r
# ==========================================================================
ax = axes[1, 1]
curve(ax, dr / 1e3, "delta_r  (km)", "6. delta_r, le pas de la boucle")
i_big = int(np.argmax(np.abs(dr)))
mark(ax, dr / 1e3, i_big, "pas le plus large",
     (3.4, dr[i_big] / 1e3 * 0.58), unit=" km")

# ==========================================================================
# 7. pressure
# ==========================================================================
ax = axes[1, 2]
curve(ax, P / GPA, "pressure  (GPa)", "7. pressure, la somme accumulee")
mark(ax, P / GPA, N - 1, "derniere ligne", (1.9, P[-1] / GPA * 0.52), unit=" GPa")
if BIG:
    j = int(np.argmin(np.abs(r - BIG[0][0])))
    mark(ax, P / GPA, j, f"r = {BIG[0][0] / 1e3:,.0f} km".replace(",", " "),
         (4.7, P[j] / GPA * 0.55), unit=" GPa")

# ==========================================================================
# 8. Les interfaces detectees
# ==========================================================================
ax = axes[1, 3]
ax.axis("off")
ax.set_title("8. Les sauts de la colonne density")
rows = ["  rayon (km)    density avant → apres", ""]
for rr, a, b in IFACES:
    rows.append(f"  {rr / 1e3:9.1f}    {a:8.1f} → {b:8.1f}")
ax.text(0.0, 0.97, "\n".join(rows), transform=ax.transAxes, fontsize=8.0,
        family="monospace", color=INK, va="top", linespacing=1.85)
ax.text(0.0, 0.97 - 0.052 * (len(rows) + 1.4),
        f"{nb(N)} lignes, du rayon terrestre a 0,1 mm du centre.\n\n"
        f"density : {rho[0]:.6g} → {rho[-1]:.6g} kg/m³\n"
        f"enclosed_mass : {m_in[0]:.6g} → {m_in[-1]:.3g} kg\n"
        f"gravitational_field : {g[0]:.6g} → {g[-1]:.3g} m/s²\n"
        f"   maximum {g.max():.6g} m/s² a r = "
        + f"{r[int(np.argmax(g))] / 1e3:,.0f} km".replace(",", " ") + "\n"
        f"pressure : {P[0] / GPA:.6g} → {P[-1] / GPA:.6g} GPa",
        transform=ax.transAxes, fontsize=8.5, color=SEC, va="top", linespacing=1.6)

fig.tight_layout(rect=(0, 0, 1, 0.955))
if "--save" in sys.argv:
    fig.savefig(os.path.join(HERE, "study_pressure_prem.png"), dpi=125,
                facecolor=SURF)
    print("study_pressure_prem.png ecrit")
plt.show()