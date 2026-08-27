"""
Fenetre 9 - PRESSION INTERNE, COUCHE PAR COUCHE
==============================================
Donnees : ../data/study_internal_pressure_without_compression_layer_by_layer
          colonnes : radius, density, delta_mass, outside_mass, enclosed_mass,
                     gravitational_field, dP/dr, delta_r, delta_P, pressure
          (le nom est cherche avec ou sans extension .csv)

Dix colonnes, tracees une par une dans l'ordre ou la boucle les calcule :

  density -> delta_mass -> outside/enclosed_mass -> gravitational_field
          -> dP/dr -> delta_r -> pressure

Note de lecture du fichier : les lignes de donnees comptent un champ de plus
que l'en-tete (elles commencent par une virgule). Le chargeur ci-dessous aligne
les colonnes sur la fin de ligne, donc les deux cas fonctionnent.

Usage :  python study_pressure_layers.py          (ouvre la fenetre)
         python study_pressure_layers.py --save   (ecrit aussi le PNG)
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
    return {c: raw[:, off + k] for k, c in enumerate(cols)}, len(cols), raw.shape[1]


def nb(n):
    return f"{n:,}".replace(",", " ")


def span(v, frac=0.10):
    lo, hi = float(np.nanmin(v)), float(np.nanmax(v))
    lo, hi = min(lo, 0.0), max(hi, 0.0)
    pad = frac * (hi - lo or abs(hi) or 1.0)
    return lo - pad, hi + pad


def curve(ax, x, y, xlabel, ylabel, title, color=BLUE, note_n=None):
    ax.plot(x, y, color=color, zorder=3)
    dress(ax, xlabel, ylabel)
    ax.set_title(title)
    ax.set_xlim(0, x.max() * 1.06)
    ax.set_ylim(*span(y))
    lo, hi = ax.get_ylim()
    if lo <= 0 <= hi:
        ax.axhline(0, color=AXIS, lw=1, zorder=2)
    if note_n:
        ax.text(0.035, 0.94, note_n, transform=ax.transAxes, color=MUTED,
                fontsize=8, va="top")
    return ax


def mark(ax, x, y, i, label, tpos, ha="left", unit="", fmt="{:.6g}"):
    ax.plot(x[i], y[i], "o", ms=7, color=BLUE, mec=SURF, mew=2, zorder=5)
    ax.annotate(f"{label}\n{fmt.format(y[i])}{unit}", xy=(x[i], y[i]), xytext=tpos,
                fontsize=8.5, color=SEC, linespacing=1.4, ha=ha, va="center",
                arrowprops=dict(arrowstyle="-", color=AXIS, lw=0.9,
                                shrinkA=2, shrinkB=6))


# --------------------------------------------------------------------------
D, n_cols, n_fields = load(
    "study_internal_pressure_without_compression_layer_by_layer")
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

# rayon ou la colonne density change de valeur, lu dans les donnees
jump = np.nonzero(np.diff(rho) != 0)[0]
R_JUMP = float(r[jump[0] + 1]) if len(jump) else None

fig, axes = plt.subplots(2, 4, figsize=(19.5, 9.3))
try:
    fig.canvas.manager.set_window_title("Gravite 9 - pression couche par couche")
except Exception:
    pass
fig.suptitle("study_internal_pressure_without_compression_layer_by_layer   —   "
             "les dix colonnes, dans l'ordre du calcul",
             fontsize=13.5, fontweight="bold", color=INK, x=0.007, ha="left", y=0.985)


def jump_line(ax):
    if R_JUMP:
        ax.axvline(R_JUMP / 1e6, color=AXIS, lw=1.2, ls=(0, (4, 3)), zorder=2)


# ==========================================================================
# 1. density
# ==========================================================================
ax = axes[0, 0]
curve(ax, r / 1e6, rho, "rayon  (1000 km)", "density  (kg/m³)",
      "1. density : deux couches", note_n=NOTE)
jump_line(ax)
if R_JUMP:
    ax.annotate(f"changement de couche\nr = {R_JUMP:.6g} m\n"
                f"{rho[-1]:.6g}  →  {rho[0]:.6g} kg/m³",
                xy=(R_JUMP / 1e6, rho[0] * 0.55), xytext=(0.85, rho[0] * 0.30),
                fontsize=8.5, color=SEC, linespacing=1.4,
                arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.1))

# ==========================================================================
# 2. delta_mass
# ==========================================================================
ax = axes[0, 1]
curve(ax, r / 1e6, dm / 1e21, "rayon  (1000 km)", "delta_mass  (10²¹ kg)",
      "2. delta_mass : la masse de chaque coquille", note_n=NOTE)
jump_line(ax)
i_dm = int(np.argmax(dm))
mark(ax, r / 1e6, dm / 1e21, i_dm, "coquille la plus lourde",
     (3.1, dm[i_dm] / 1e21 * 0.72), unit=" ×10²¹ kg")

# ==========================================================================
# 3. outside_mass et enclosed_mass
# ==========================================================================
ax = axes[0, 2]
ax.plot(r / 1e6, m_in / 1e24, color=BLUE, zorder=3, label="enclosed_mass")
ax.plot(r / 1e6, m_out / 1e24, color=ORANGE, zorder=3, label="outside_mass")
dress(ax, "rayon  (1000 km)", "masse  (10²⁴ kg)")
ax.set_title("3. enclosed_mass et outside_mass")
ax.set_xlim(0, R_SURF / 1e6 * 1.06)
ax.set_ylim(*span(np.concatenate([m_in, m_out]) / 1e24))
jump_line(ax)
ax.legend(loc="center left")
ax.text(0.035, 0.94, NOTE, transform=ax.transAxes, color=MUTED, fontsize=8,
        va="top")
ax.text(0.06, 0.30, f"les deux se somment a\n{(m_in[0] + m_out[0]) / 1e24:.6g}·10²⁴ kg\n"
                    "sur chaque ligne.",
        transform=ax.transAxes, ha="left", color=SEC, fontsize=8,
        linespacing=1.5, va="top")

# ==========================================================================
# 4. gravitational_field
# ==========================================================================
ax = axes[0, 3]
curve(ax, r / 1e6, g, "rayon  (1000 km)", "gravitational_field  (m/s²)",
      "4. gravitational_field", note_n=NOTE)
jump_line(ax)
mark(ax, r / 1e6, g, 0, "1re ligne", (3.4, g[0] * 0.80), unit=" m/s²")
if R_JUMP:
    j = int(np.argmin(np.abs(r - R_JUMP)))
    mark(ax, r / 1e6, g, j, "au changement\nde couche", (1.05, g[j] * 1.85),
         unit=" m/s²")

# ==========================================================================
# 5. dP/dr
# ==========================================================================
ax = axes[1, 0]
curve(ax, r / 1e6, dpdr / 1e3, "rayon  (1000 km)", "dP/dr  (kPa par metre)",
      "5. dP/dr", note_n=NOTE)
jump_line(ax)
if R_JUMP:
    j = int(np.argmin(np.abs(r - R_JUMP)))
    ax.annotate(f"{dpdr[j - 1] / 1e3:.6g}  →  {dpdr[j] / 1e3:.6g} kPa/m",
                xy=(R_JUMP / 1e6, (dpdr[j - 1] + dpdr[j]) / 2e3),
                xytext=(0.35, dpdr.min() / 1e3 * 0.55),
                fontsize=8.5, color=SEC, linespacing=1.4,
                arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.1))
mark(ax, r / 1e6, dpdr / 1e3, 0, "1re ligne", (3.9, dpdr.min() / 1e3 * 0.22),
     unit=" kPa/m")

# ==========================================================================
# 6. delta_r
# ==========================================================================
ax = axes[1, 1]
curve(ax, r / 1e6, dr / 1e3, "rayon  (1000 km)", "delta_r  (km)",
      "6. delta_r, le pas de la boucle", note_n=NOTE)
i_big = int(np.argmax(np.abs(dr)))
mark(ax, r / 1e6, dr / 1e3, i_big, "pas le plus large",
     (3.5, dr[i_big] / 1e3 * 0.60), unit=" km")

# ==========================================================================
# 7. pressure
# ==========================================================================
ax = axes[1, 2]
curve(ax, r / 1e6, P / GPA, "rayon  (1000 km)", "pressure  (GPa)",
      "7. pressure, la somme accumulee", note_n=NOTE)
jump_line(ax)
mark(ax, r / 1e6, P / GPA, N - 1, "derniere ligne", (1.7, P[-1] / GPA * 0.50),
     unit=" GPa")
if R_JUMP:
    j = int(np.argmin(np.abs(r - R_JUMP)))
    mark(ax, r / 1e6, P / GPA, j, "au changement\nde couche",
         (4.9, P[j] / GPA * 0.42), unit=" GPa")

# ==========================================================================
# 8. Extrait du fichier
# ==========================================================================
ax = axes[1, 3]
ax.axis("off")
ax.set_title("8. Ce qu'il y a dans le fichier")
rows = ["radius       density  enclosed_mass  g        pressure", ""]
picks = [(0, "1re ligne"), (1, "2e ligne")]
if R_JUMP:
    j = int(np.argmin(np.abs(r - R_JUMP)))
    picks += [(j - 1, "avant couche"), (j, "apres couche")]
picks += [(int(np.argmin(np.abs(r - 1e6))), "1 000 km"),
          (int(np.argmin(np.abs(r - 1e3))), "1 km"), (N - 1, "derniere")]
for i, tag in picks:
    rows.append(f"{r[i]:<12.6g} {rho[i]:<8.6g} {m_in[i]:<14.6g} "
                f"{g[i]:<8.6g} {P[i]:<12.6g} {tag}")
ax.text(0.0, 0.97, "\n".join(rows), transform=ax.transAxes, fontsize=7.4,
        family="monospace", color=INK, va="top", linespacing=1.85)
ax.text(0.0, 0.50,
        f"{nb(N)} lignes, du rayon terrestre a 1 mm du centre.\n\n"
        f"pressure : {P[0] / GPA:.6g} → {P[-1] / GPA:.6g} GPa\n"
        f"gravitational_field : {g[0]:.6g} → {g[-1]:.3g} m/s²\n"
        f"enclosed_mass : {m_in[0]:.6g} → {m_in[-1]:.3g} kg\n\n"
        f"L'en-tete annonce {n_cols} colonnes, les lignes de\n"
        f"donnees en contiennent {n_fields} : le champ en trop\n"
        "est en debut de ligne et le chargeur l'ignore.",
        transform=ax.transAxes, fontsize=8.5, color=SEC, va="top", linespacing=1.6)

fig.tight_layout(rect=(0, 0, 1, 0.955))
if "--save" in sys.argv:
    fig.savefig(os.path.join(HERE, "study_pressure_layers.png"), dpi=125,
                facecolor=SURF)
    print("study_pressure_layers.png ecrit")
plt.show()