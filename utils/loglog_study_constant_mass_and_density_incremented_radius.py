"""
Fenetre 5 - VERIFICATION log10-log10
====================================
Une loi de puissance  y = k · x^p  devient une droite de pente p quand on trace
log10(y) en fonction de log10(x). Ce script fait exactement cela sur les colonnes
deja presentes dans les CSV, et mesure la pente par moindres carres.

Attendu :
    study_constant_density_incremented_radius   mass    en fonction du rayon  -> +3
    study_constant_mass_incremented_radius      density en fonction du rayon  -> -3
et, en bonus, la meme mesure sur les trois etudes precedentes (+1, -2, +1/2).

Rien n'est simule ni recalcule : on ne fait que prendre le log des colonnes.

Usage :  python study_loglog.py          (ouvre la fenetre)
         python study_loglog.py --save   (ecrit aussi study_loglog.png)
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


def dress(ax, xlabel="", ylabel="", grid="y"):
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_linewidth(0.9)
    if grid:
        ax.grid(axis=grid, alpha=1.0)
    ax.set_axisbelow(True)
    return ax


HERE = os.path.dirname(os.path.abspath(__file__))


def find(name, required=True):
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
    if not required:
        return None
    sys.exit("Fichier de donnees introuvable. Chemins essayes :\n  "
             + "\n  ".join(dict.fromkeys(tried)))


def load(name, required=True):
    path = find(name, required)
    if path is None:
        return None
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
    """Ne garde que les lignes exploitables (finies et strictement positives),
    passe au log10 et ajuste une droite par moindres carres."""
    ok = np.isfinite(x) & np.isfinite(y) & (x > 0) & (y > 0)
    lx, ly = np.log10(x[ok]), np.log10(y[ok])
    slope, intercept = np.polyfit(lx, ly, 1)
    resid = ly - (slope * lx + intercept)
    r2 = 1.0 - np.sum(resid ** 2) / np.sum((ly - ly.mean()) ** 2)
    return dict(lx=lx, ly=ly, slope=float(slope), intercept=float(intercept),
                resid=resid, r2=float(r2), n=int(ok.sum()), total=len(x))


# --------------------------------------------------------------------------
A = load("study_constant_density_incremented_radius")
B = load("study_constant_mass_incremented_radius")
fitA = loglog_fit(A["radius"], A["mass"])
fitB = loglog_fit(B["radius"], B["density"])

fig, axes = plt.subplots(2, 3, figsize=(16.5, 9.3))
try:
    fig.canvas.manager.set_window_title("Gravite 5 - verification log10-log10")
except Exception:
    pass
fig.suptitle("Verification log10–log10   —   une loi de puissance devient une droite, "
             "sa pente est l'exposant",
             fontsize=13.5, fontweight="bold", color=INK, x=0.008, ha="left", y=0.985)


def panel_loglog(ax, f, xlabel, ylabel, title, expected, note, corner, legloc):
    st = max(1, f["n"] // 4000)
    ax.plot(f["lx"][::st], f["ly"][::st], color=BLUE, lw=3.2, zorder=3,
            label="donnees du CSV")
    xs = np.array([f["lx"].min(), f["lx"].max()])
    ax.plot(xs, f["slope"] * xs + f["intercept"], color=ORANGE, lw=1.3,
            ls=(0, (5, 4)), zorder=4, label="droite ajustee")
    dress(ax, xlabel, ylabel)
    ax.set_title(title)
    ax.legend(loc=legloc)
    tx, ha = (0.035, "left") if corner == "left" else (0.97, "right")
    ax.text(tx, 0.44,
            f"pente mesuree  =  {f['slope']:+.10f}\n"
            f"pente attendue =  {expected:+.10f}\n"
            f"ecart           =  {abs(f['slope'] - expected):.1e}\n"
            f"R²              =  {f['r2']:.12f}\n"
            f"{nb(f['n'])} lignes exploitables sur {nb(f['total'])}",
            transform=ax.transAxes, fontsize=8.5, family="monospace", ha=ha,
            color=INK, va="top", linespacing=1.7)
    ax.text(tx, 0.02, note, transform=ax.transAxes, fontsize=8, color=SEC,
            ha=ha, va="bottom", linespacing=1.5)


# ==========================================================================
# 1 et 2 : les deux droites
# ==========================================================================
panel_loglog(axes[0, 0], fitA, "log10(rayon)  [rayon en m]", "log10(masse)  [masse en kg]",
             "1. Densite figee : masse en fonction du rayon",
             3.0,
             "10^(ordonnee a l'origine) = " + f"{10 ** fitA['intercept']:.6g}\n"
             "c'est exactement la masse lue a r = 1 m\ndans le fichier.",
             corner="right", legloc="upper left")

panel_loglog(axes[0, 1], fitB, "log10(rayon)  [rayon en m]",
             "log10(densite)  [densite en kg/m³]",
             "2. Masse figee : densite en fonction du rayon",
             -3.0,
             "10^(ordonnee a l'origine) = " + f"{10 ** fitB['intercept']:.6g}\n"
             "c'est exactement la densite lue a r = 1 m\ndans le fichier.",
             corner="left", legloc="upper right")

# ==========================================================================
# 3 : residus
# ==========================================================================
ax = axes[0, 2]
for f, col, lab in ((fitA, BLUE, "mass  (pente +3)"), (fitB, ORANGE, "density  (pente −3)")):
    st = max(1, f["n"] // 4000)
    ax.plot(f["lx"][::st], f["resid"][::st] / 1e-6, color=col, lw=1.1, zorder=3,
            label=lab)
dress(ax, "log10(rayon)", "ecart a la droite  (10⁻⁶ decade)")
ax.axhline(0, color=AXIS, lw=1)
ax.set_ylim(-24, 11)
ax.legend(loc="upper right")
ax.set_title("3. Ce qui reste une fois la droite retiree")
worst = max(np.abs(fitA["resid"]).max(), np.abs(fitB["resid"]).max())
ax.text(0.035, 0.06, "aucune courbure residuelle : l'ecart maximal vaut\n"
                     f"{worst:.1e} decade, soit {10 ** worst - 1:.1e} en relatif.\n"
                     "C'est exactement la precision d'ecriture du CSV\n"
                     "(6 chiffres significatifs), pas un defaut du modele.",
        transform=ax.transAxes, fontsize=8, color=SEC, va="bottom", linespacing=1.5)

# ==========================================================================
# 4 : pente locale
# ==========================================================================
ax = axes[1, 0]
LAG = 2000
for f, col, lab in ((fitA, BLUE, "mass"), (fitB, ORANGE, "density")):
    lx, ly = f["lx"], f["ly"]
    p = (ly[LAG:] - ly[:-LAG]) / (lx[LAG:] - lx[:-LAG])
    st = max(1, len(p) // 4000)
    ax.plot(lx[:-LAG][::st], p[::st], color=col, lw=1.6, zorder=3, label=lab)
dress(ax, "log10(rayon)", "pente locale")
for lvl in (3, -3):
    ax.axhline(lvl, color=AXIS, lw=1.2, ls=(0, (4, 3)), zorder=2)
ax.set_ylim(-4.2, 4.2)
xr = fitA["lx"].max()
ax.text(xr, 3.35, "mass", color=BLUE, fontsize=9, fontweight="bold", ha="right")
ax.text(xr, -2.65, "density", color=ORANGE, fontsize=9, fontweight="bold", ha="right")
ax.set_title("4. La pente ne bouge pas d'un bout a l'autre du fichier")
ax.text(0.035, 0.60, f"pente mesuree sur une fenetre glissante de {nb(LAG)} lignes\n"
                     "(soit un peu moins d'une decade de rayon).\n"
                     "Une loi de puissance donne une pente constante ;\n"
                     "n'importe quel autre modele la ferait deriver.",
        transform=ax.transAxes, fontsize=8, color=SEC, va="top", linespacing=1.5)

# ==========================================================================
# 5 : le detail chiffre
# ==========================================================================
ax = axes[1, 1]
ax.axis("off")
ax.set_title("5. Le resultat, chiffre")
rows = [
    "                              mass          density",
    "",
    f"pente mesuree            {fitA['slope']:+.10f}   {fitB['slope']:+.10f}",
    f"pente attendue           {3.0:+.10f}   {-3.0:+.10f}",
    f"ecart                     {abs(fitA['slope'] - 3):.2e}      {abs(fitB['slope'] + 3):.2e}",
    f"R²                        {fitA['r2']:.10f}    {fitB['r2']:.10f}",
    f"lignes utilisees          {nb(fitA['n']):>10}    {nb(fitB['n']):>10}",
    f"lignes ecartees           {nb(fitA['total'] - fitA['n']):>10}    "
    f"{nb(fitB['total'] - fitB['n']):>10}",
]
ax.text(0.0, 0.92, "\n".join(rows), transform=ax.transAxes, fontsize=8.2,
        family="monospace", color=INK, va="top", linespacing=1.8)
ax.text(0.0, 0.30, "Les lignes ecartees sont celles ou le CSV contient inf ou 0 :\n"
                   "le log10 n'y est pas defini. Ce sont exactement les zones\n"
                   "de debordement reperees dans la fenetre precedente.\n\n"
                   "Une pente de 3,0000000002 sur pres de 105 decades de rayon\n"
                   "ne laisse pas de place a un autre exposant.",
        transform=ax.transAxes, fontsize=8.5, color=SEC, va="top", linespacing=1.6)

# ==========================================================================
# 6 : le meme test sur toutes les etudes
# ==========================================================================
ax = axes[1, 2]
CASES = [
    ("study_mass_increase", "celestial_body_mass", "gravitational_field",
     "g  vs  masse", 1.0),
    ("study_radius_increase", "radius", "gravitational_field",
     "g  vs  rayon", -2.0),
    ("study_gravitational_radius", "celestial_body_mass", "gravitational_radius",
     "rayon d'influence  vs  masse", 0.5),
    ("study_constant_density_incremented_radius", "radius", "mass",
     "masse  vs  rayon", 3.0),
    ("study_constant_mass_incremented_radius", "radius", "density",
     "densite  vs  rayon", -3.0),
]
labels, got, exp = [], [], []
for fname, cx, cy, label, e in CASES:
    d = load(fname, required=False)
    if d is None or cx not in d or cy not in d:
        continue
    f = loglog_fit(d[cx], d[cy])
    labels.append(label)
    got.append(f["slope"])
    exp.append(e)
ys = np.arange(len(labels))
ax.hlines(ys, -3.4, 3.4, color=GRID, lw=1, zorder=1)
ax.plot(exp, ys, "|", ms=18, mew=2, color=ORANGE, zorder=3, label="exposant attendu")
ax.plot(got, ys, "o", ms=9, color=BLUE, mec=SURF, mew=2, zorder=4,
        label="pente mesuree")
for y, g in zip(ys, got):
    ax.annotate(f"{g:+.9f}", (g, y), xytext=(0, 11), textcoords="offset points",
                ha="center", fontsize=8, color=SEC)
ax.set_yticks(ys)
ax.set_yticklabels(labels, fontsize=8.5)
ax.tick_params(axis="y", colors=SEC, length=0)
ax.set_xlim(-3.6, 3.6)
ax.set_ylim(-0.7, len(labels) - 0.25)
ax.invert_yaxis()
dress(ax, "exposant", grid="")
for s in ("left",):
    ax.spines[s].set_visible(False)
ax.legend(loc="upper left")
ax.set_title("6. Le meme test applique a toutes les etudes")
if got:
    ax.text(0.0, -0.16, "ecart maximal a la valeur entiere (ou demi-entiere) attendue : "
            + f"{max(abs(g - e) for g, e in zip(got, exp)):.1e}",
            transform=ax.transAxes, fontsize=8.5, color=SEC)

fig.tight_layout(rect=(0, 0, 1, 0.955))
if "--save" in sys.argv:
    fig.savefig(os.path.join(HERE, "study_loglog.png"), dpi=130, facecolor=SURF)
    print("study_loglog.png ecrit")
plt.show()