"""
Fenetre 7 - A L'INTERIEUR DE LA SPHERE
======================================
Donnees : ../data/study_distance_from_center_effect_inside_uniform_sphere
          (distance_from_center : 0,001 m -> rayon terrestre, *1.001)
          + en option ../data/study_radius_increase, pour prolonger le profil
            au-dela de la surface (le panneau 2 est saute si le fichier manque)

Contrairement aux autres etudes, celle-ci ne parcourt que 10 decades : elle
s'arrete au rayon terrestre. Elle tient donc presque entierement dans un seul
trace lineaire.

Ligne du haut : les colonnes du CSV en axes lineaires.
Ligne du bas  : les memes colonnes en log10-log10, avec la pente mesuree.

Usage :  python study_inside_sphere.py          (ouvre la fenetre)
         python study_inside_sphere.py --save   (ecrit aussi le PNG)
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
    ok = np.isfinite(x) & np.isfinite(y) & (x > 0) & (y > 0)
    lx, ly = np.log10(x[ok]), np.log10(y[ok])
    slope, intercept = np.polyfit(lx, ly, 1)
    resid = ly - (slope * lx + intercept)
    return dict(lx=lx, ly=ly, slope=float(slope), intercept=float(intercept),
                worst=float(np.abs(resid).max()), n=int(ok.sum()), total=len(x))


# --------------------------------------------------------------------------
D = load("study_distance_from_center_effect_inside_uniform_sphere")
r, m_in, g_in = (D["distance_from_center"], D["enclosed_mass"],
                 D["gravitational_field"])
N = len(r)
R_SURF = float(r[-1])            # derniere ligne = le rayon terrestre atteint

OUT = load("study_radius_increase", required=False)

fg = loglog_fit(r, g_in)
fm = loglog_fit(r, m_in)

fig, axes = plt.subplots(2, 3, figsize=(16.5, 9.3))
try:
    fig.canvas.manager.set_window_title("Gravite 7 - a l'interieur de la sphere")
except Exception:
    pass
fig.suptitle("study_distance_from_center_effect_inside_uniform_sphere   —   "
             "le champ sous la surface",
             fontsize=13.5, fontweight="bold", color=INK, x=0.008, ha="left", y=0.985)


def readout(ax, x, y, target, label, unit, tpos, ha="left"):
    i = int(np.argmin(np.abs(x - target)))
    ax.plot(x[i] / ax._xdiv, y[i] / ax._ydiv, "o", ms=7, color=BLUE,
            mec=SURF, mew=2, zorder=5)
    ax.annotate(f"{label}\n{y[i]:.4g} {unit}",
                xy=(x[i] / ax._xdiv, y[i] / ax._ydiv), xytext=tpos,
                fontsize=8.5, color=SEC, linespacing=1.4, ha=ha, va="center",
                arrowprops=dict(arrowstyle="-", color=AXIS, lw=0.9,
                                shrinkA=2, shrinkB=6))


def loglog_panel(ax, f, ylabel, title, expected, note):
    st = max(1, f["n"] // 4000)
    ax.plot(f["lx"][::st], f["ly"][::st], color=BLUE, lw=3.2, zorder=3,
            label="donnees du CSV")
    xs = np.array([f["lx"].min(), f["lx"].max()])
    ax.plot(xs, f["slope"] * xs + f["intercept"], color=ORANGE, lw=1.3,
            ls=(0, (5, 4)), zorder=4, label="droite ajustee")
    dress(ax, "log10(distance au centre)  [en m]", ylabel)
    ax.set_title(title)
    ax.legend(loc="upper left")
    ax.text(0.97, 0.44,
            f"pente mesuree  =  {f['slope']:.10f}\n"
            f"pente attendue =  {expected:.10f}\n"
            f"ecart           =  {abs(f['slope'] - expected):.1e}\n"
            f"ecart max a la droite = {f['worst']:.1e} decade\n"
            f"{nb(f['n'])} lignes sur {nb(f['total'])}",
            transform=ax.transAxes, fontsize=8.5, family="monospace", ha="right",
            color=INK, va="top", linespacing=1.7)
    ax.text(0.97, 0.02, note, transform=ax.transAxes, fontsize=8, color=SEC,
            ha="right", va="bottom", linespacing=1.5)


# ==========================================================================
# 1. Le champ en descendant vers le centre
# ==========================================================================
ax = axes[0, 0]
ax._xdiv, ax._ydiv = 1e6, 1.0
ax.plot(r / 1e6, g_in, color=BLUE, zorder=3)
dress(ax, "distance au centre  (1000 km)", "g  (m/s²)")
ax.set_xlim(0, 6.8)
ax.set_ylim(0, 11.5)
ax.set_title("1. Sous la surface, g redescend vers zero")
ax.text(0.035, 0.93, f"{nb(N)} lignes — tout le fichier",
        transform=ax.transAxes, color=MUTED, fontsize=8, va="top")
readout(ax, r, g_in, R_SURF, "surface", "m/s²", (4.15, 10.6))
readout(ax, r, g_in, 3.48e6, "limite noyau / manteau\n(3 480 km)", "m/s²", (2.1, 7.4))
readout(ax, r, g_in, 1.22e6, "rayon de la graine\n(1 220 km)", "m/s²", (1.75, 3.3))
ax.text(0.97, 0.06, "modele de densite uniforme : g est proportionnel\n"
                    "a la distance au centre, et s'annule au centre.\n"
                    "(dans la vraie Terre, plus dense au coeur, g reste\n"
                    "proche de 10 jusqu'au noyau avant de retomber.)",
        transform=ax.transAxes, ha="right", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

# ==========================================================================
# 2. Le profil complet, en recollant l'etude sur le rayon
# ==========================================================================
ax = axes[0, 1]
ax._xdiv, ax._ydiv = 1e6, 1.0
ax.plot(r / 1e6, g_in, color=BLUE, zorder=3, label="interieur (ce fichier)")
if OUT is not None:
    ro, go = OUT["radius"], OUT["gravitational_field"]
    sel = (ro >= R_SURF) & (ro <= 2.4e7) & np.isfinite(go)
    ax.plot(ro[sel] / 1e6, go[sel], color=ORANGE, zorder=3,
            label="exterieur (study_radius_increase)")
    ax.legend(loc="upper right")
ax.axvline(R_SURF / 1e6, color=AXIS, lw=1.2, ls=(0, (4, 3)), zorder=2)
dress(ax, "distance au centre  (1000 km)", "g  (m/s²)")
ax.set_xlim(0, 24)
ax.set_ylim(0, 11.5)
ax.set_title("2. Le profil entier : montee, pic, decroissance")
ax.annotate("maximum exactement\na la surface", xy=(R_SURF / 1e6, 9.82),
            xytext=(9.6, 7.4), fontsize=8.5, color=SEC, linespacing=1.4,
            arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.1))
if OUT is None:
    ax.text(0.5, 0.5, "study_radius_increase absent :\nseule la partie interieure est tracee",
            transform=ax.transAxes, ha="center", color=MUTED, fontsize=9,
            linespacing=1.5)
else:
    ax.text(0.97, 0.06, "deux fichiers differents, tracables sur le meme axe\n"
                        "parce qu'ils sont dans la meme unite. Ils se rejoignent\n"
                        "a la surface sans raccord force.",
            transform=ax.transAxes, ha="right", color=SEC, fontsize=8,
            linespacing=1.5, va="bottom")

# ==========================================================================
# 3. La masse contenue sous les pieds
# ==========================================================================
ax = axes[0, 2]
ax._xdiv, ax._ydiv = 1e6, 1e24
ax.plot(r / 1e6, m_in / 1e24, color=BLUE, zorder=3)
dress(ax, "distance au centre  (1000 km)", "masse contenue  (10²⁴ kg)")
ax.set_xlim(0, 6.8)
ax.set_ylim(0, 7.2)
ax.set_title("3. La masse contenue suit le cube de la distance")
ax.text(0.035, 0.93, f"{nb(N)} lignes — tout le fichier",
        transform=ax.transAxes, color=MUTED, fontsize=8, va="top")
readout(ax, r, m_in, R_SURF, "surface", "kg", (4.0, 6.5))
readout(ax, r, m_in, 3.48e6, "limite noyau / manteau", "kg", (1.5, 2.6))
ax.text(0.97, 0.06, "a mi-rayon il n'y a qu'un huitieme de la masse\n"
                    "sous les pieds — mais la distance est deux fois\n"
                    "plus petite, d'ou un g deux fois plus faible et\n"
                    "non huit fois.",
        transform=ax.transAxes, ha="right", color=SEC, fontsize=8,
        linespacing=1.5, va="bottom")

# ==========================================================================
# 4 et 5 : les pentes
# ==========================================================================
loglog_panel(axes[1, 0], fg, "log10(g)  [g en m/s²]",
             "4. Le champ en log10–log10", 1.0,
             "10^(ordonnee a l'origine) = " + f"{10 ** fg['intercept']:.6g}\n"
             "c'est la valeur de g a 1 m du centre,\nlue dans le fichier.")

loglog_panel(axes[1, 1], fm, "log10(masse contenue)  [en kg]",
             "5. La masse contenue en log10–log10", 3.0,
             "10^(ordonnee a l'origine) = " + f"{10 ** fm['intercept']:.6g}\n"
             "c'est la masse contenue dans une sphere\nde 1 m de rayon.")

# ==========================================================================
# 6. Extrait du fichier
# ==========================================================================
ax = axes[1, 2]
ax.axis("off")
ax.set_title("6. Ce qu'il y a dans le fichier")
rows = ["distance      enclosed_mass  gravitational_field", ""]
for target, tag in [(1e-3, "1re ligne"), (1.0, "1 m"), (1e3, "1 km"),
                    (1.22e6, "graine"), (3.48e6, "noyau"), (R_SURF, "surface")]:
    i = int(np.argmin(np.abs(r - target)))
    rows.append(f"{r[i]:<13.6g} {m_in[i]:<14.6g} {g_in[i]:<12.6g} {tag}")
ax.text(0.0, 0.90, "\n".join(rows), transform=ax.transAxes, fontsize=8.2,
        family="monospace", color=INK, va="top", linespacing=1.8)
bad = int((~np.isfinite(g_in)).sum() + (g_in == 0).sum()
          + (~np.isfinite(m_in)).sum() + (m_in == 0).sum())
ax.text(0.0, 0.40,
        f"{nb(N)} lignes, de 1 mm au rayon terrestre :\n"
        "un peu moins de 10 decades, contre 300 a 600\n"
        "pour les autres etudes. C'est la seule qui a\n"
        "une borne physique et non une borne de boucle.\n\n"
        + (f"{nb(bad)} valeurs nulles ou infinies."
           if bad else "Aucune valeur nulle ni infinie : la plage est\n"
                       "trop courte pour inquieter un double."),
        transform=ax.transAxes, fontsize=8.5, color=SEC, va="top", linespacing=1.6)

fig.tight_layout(rect=(0, 0, 1, 0.955))
if "--save" in sys.argv:
    fig.savefig(os.path.join(HERE, "study_inside_sphere.png"), dpi=130, facecolor=SURF)
    print("study_inside_sphere.png ecrit")
plt.show()