"""
Geração de Gráficos — Heurística Greedy Addition para o P-Median
=================================================================
Disciplina: SIN-492 - Inteligência Computacional
Universidade Federal de Viçosa - Campus Rio Paranaíba

Execute este script APÓS rodar p_median_greedy.py.
Os gráficos serão salvos na pasta 'graficos/' como arquivos PNG.

Aluno(a): <seu nome>
Matrícula: <sua matrícula>
"""

import os
import math
import time
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# =============================================================================
# DADOS DOS RESULTADOS (copiados da saída do p_median_greedy.py)
# =============================================================================

resultados = [
    # (inst, n, p, otimo, heuristica, gap, tempo)
    (1,  100,   5,  5819.0,  5814.0, -0.09,  0.004),
    (2,  100,  10,  4093.0,  4315.0,  5.42,  0.008),
    (3,  100,  10,  4250.0,  4572.0,  7.58,  0.008),
    (4,  100,  20,  3034.0,  3039.0,  0.16,  0.017),
    (5,  100,  33,  1355.0,  1378.0,  1.70,  0.025),
    (6,  200,   5,  7824.0,  7890.0,  0.84,  0.020),
    (7,  200,  10,  5631.0,  5706.0,  1.33,  0.042),
    (8,  200,  20,  4445.0,  4517.0,  1.62,  0.075),
    (9,  200,  40,  2734.0,  2784.0,  1.83,  0.142),
    (10, 200,  67,  1255.0,  1293.0,  3.03,  0.218),
    (11, 300,   5,  7696.0,  7897.0,  2.61,  0.083),
    (12, 300,  10,  6634.0,  6701.0,  1.01,  0.169),
    (13, 300,  30,  4374.0,  4439.0,  1.49,  0.428),
    (14, 300,  60,  2968.0,  3006.0,  1.28,  0.847),
    (15, 300, 100,  1729.0,  1725.0, -0.23,  1.137),
    (16, 400,   5,  8162.0,  8315.0,  1.87,  0.136),
    (17, 400,  10,  6999.0,  7091.0,  1.31,  0.257),
    (18, 400,  40,  4809.0,  4726.0, -1.73,  1.000),
    (19, 400,  80,  2845.0,  2897.0,  1.83,  1.818),
    (20, 400, 133,  1789.0,  1845.0,  3.13,  2.774),
    (21, 500,   5,  9138.0,  9495.0,  3.91,  0.225),
    (22, 500,   5,  8579.0,  9495.0, 10.68,  0.233),
    (23, 500,  50,  4619.0,  4590.0, -0.63,  2.141),
    (24, 500, 100,  2961.0,  2946.0, -0.51,  3.991),
    (25, 500, 167,  1828.0,  1877.0,  2.68,  7.075),
    (26, 600,   5,  9917.0,  9965.0,  0.48,  0.366),
    (27, 600,  10,  8307.0,  8338.0,  0.37,  0.731),
    (28, 600,  60,  4498.0,  4503.0,  0.11,  4.047),
    (29, 600, 120,  3033.0,  3069.0,  1.19,  7.740),
    (30, 600, 200,  1989.0,  1991.0,  0.10, 12.923),
    (31, 700,   5, 10086.0, 10339.0,  2.51,  0.466),
    (32, 700,  10,  9297.0,  9447.0,  1.61,  0.983),
    (33, 700,  70,  4700.0,  4712.0,  0.26,  7.088),
    (34, 700, 140,  3013.0,  2998.0, -0.50, 13.104),
    (35, 800,   5, 10400.0, 10491.0,  0.88,  0.718),
    (36, 800,  10,  9934.0, 10041.0,  1.08,  1.428),
    (37, 800,  80,  5057.0,  5051.0, -0.12, 11.104),
    (38, 900,   5, 11060.0, 11343.0,  2.56,  0.885),
    (39, 900,  10,  9423.0,  9575.0,  1.61,  1.825),
    (40, 900,  90,  5128.0,  5122.0, -0.12, 16.088),
]

# Extrai colunas individuais
instancias = [r[0] for r in resultados]
ns         = [r[1] for r in resultados]
ps         = [r[2] for r in resultados]
otimos     = [r[3] for r in resultados]
heuristicas= [r[4] for r in resultados]
gaps       = [r[5] for r in resultados]
tempos     = [r[6] for r in resultados]

# =============================================================================
# CONFIGURAÇÕES GERAIS DE ESTILO
# =============================================================================

plt.rcParams.update({
    'font.family':     'DejaVu Sans',
    'font.size':       11,
    'axes.titlesize':  13,
    'axes.labelsize':  11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'axes.grid':       True,
    'grid.alpha':      0.35,
    'grid.linestyle':  '--',
    'figure.dpi':      150,
})

COR_HEUR  = '#2196F3'   # azul  — heurística
COR_OT    = '#4CAF50'   # verde — ótimo
COR_POS   = '#F44336'   # vermelho — gap positivo (acima do ótimo)
COR_NEG   = '#4CAF50'   # verde    — gap negativo (abaixo do ótimo)
COR_TEMPO = '#9C27B0'   # roxo  — tempo

os.makedirs('graficos', exist_ok=True)

# =============================================================================
# GRÁFICO 1 — Gap (%) por Instância
# =============================================================================

fig, ax = plt.subplots(figsize=(14, 5))

cores_barra = [COR_NEG if g <= 0 else COR_POS for g in gaps]
barras = ax.bar(instancias, gaps, color=cores_barra, edgecolor='white',
                linewidth=0.5, zorder=3)

ax.axhline(0, color='black', linewidth=0.8, linestyle='-', zorder=4)
ax.axhline(sum(gaps)/len(gaps), color='#FF9800', linewidth=1.5,
           linestyle='--', zorder=4, label=f'Gap médio: {sum(gaps)/len(gaps):.2f}%')

ax.set_xlabel('Instância')
ax.set_ylabel('Gap (%)')
ax.set_title('Gap percentual da heurística Greedy Addition em relação ao ótimo\n(OR-Library — pmed1 a pmed40)')
ax.set_xticks(instancias)
ax.set_xticklabels([str(i) for i in instancias], rotation=90, fontsize=8)

patch_pos = mpatches.Patch(color=COR_POS, label='Acima do ótimo')
patch_neg = mpatches.Patch(color=COR_NEG, label='Abaixo/igual ao ótimo')
ax.legend(handles=[patch_pos, patch_neg,
          plt.Line2D([0],[0], color='#FF9800', lw=1.5, linestyle='--',
                     label=f'Gap médio: {sum(gaps)/len(gaps):.2f}%')],
          loc='upper right', fontsize=9)

plt.tight_layout()
plt.savefig('graficos/01_gap_por_instancia.png')
plt.close()
print("Gráfico 1 salvo: graficos/01_gap_por_instancia.png")

# =============================================================================
# GRÁFICO 2 — Valor da Heurística vs Ótimo por Instância
# =============================================================================

fig, ax = plt.subplots(figsize=(14, 5))

ax.plot(instancias, otimos,     color=COR_OT,   marker='o', markersize=4,
        linewidth=1.5, label='Valor ótimo', zorder=3)
ax.plot(instancias, heuristicas, color=COR_HEUR, marker='s', markersize=4,
        linewidth=1.5, linestyle='--', label='Greedy Addition', zorder=3)

ax.fill_between(instancias, otimos, heuristicas,
                alpha=0.12, color=COR_HEUR, zorder=2)

ax.set_xlabel('Instância')
ax.set_ylabel('Custo da solução')
ax.set_title('Comparação entre valor ótimo e heurística Greedy Addition\n(pmed1 a pmed40)')
ax.set_xticks(instancias)
ax.set_xticklabels([str(i) for i in instancias], rotation=90, fontsize=8)
ax.legend(fontsize=10)

plt.tight_layout()
plt.savefig('graficos/02_heuristica_vs_otimo.png')
plt.close()
print("Gráfico 2 salvo: graficos/02_heuristica_vs_otimo.png")

# =============================================================================
# GRÁFICO 3 — Tempo de Execução por Instância
# =============================================================================

fig, ax = plt.subplots(figsize=(14, 5))

ax.bar(instancias, tempos, color=COR_TEMPO, edgecolor='white',
       linewidth=0.5, zorder=3, alpha=0.85)

ax.set_xlabel('Instância')
ax.set_ylabel('Tempo (segundos)')
ax.set_title('Tempo de execução da heurística Greedy Addition por instância\n(pmed1 a pmed40)')
ax.set_xticks(instancias)
ax.set_xticklabels([str(i) for i in instancias], rotation=90, fontsize=8)

plt.tight_layout()
plt.savefig('graficos/03_tempo_por_instancia.png')
plt.close()
print("Gráfico 3 salvo: graficos/03_tempo_por_instancia.png")

# =============================================================================
# GRÁFICO 4 — Tempo de Execução vs Tamanho n (escala log)
# =============================================================================

fig, ax = plt.subplots(figsize=(8, 5))

scatter = ax.scatter(ns, tempos, c=ps, cmap='plasma', s=60,
                     edgecolors='white', linewidths=0.5, zorder=3)

cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Valor de p', fontsize=10)

# Linha de tendência (regressão polinomial grau 2 em log-log)
ns_arr = np.array(ns, dtype=float)
ts_arr = np.array(tempos, dtype=float)
log_n  = np.log(ns_arr)
log_t  = np.log(ts_arr + 1e-6)
coef   = np.polyfit(log_n, log_t, 1)
xs     = np.linspace(min(ns_arr), max(ns_arr), 200)
ys     = np.exp(np.polyval(coef, np.log(xs)))
ax.plot(xs, ys, color='#FF9800', linewidth=1.5, linestyle='--',
        label=f'Tendência (exp={coef[0]:.2f})', zorder=4)

ax.set_xlabel('Número de vértices (n)')
ax.set_ylabel('Tempo (segundos)')
ax.set_title('Tempo de execução × tamanho do problema\n(cor indica valor de p)')
ax.legend(fontsize=9)

plt.tight_layout()
plt.savefig('graficos/04_tempo_vs_n.png')
plt.close()
print("Gráfico 4 salvo: graficos/04_tempo_vs_n.png")

# =============================================================================
# GRÁFICO 5 — Gap (%) vs Razão p/n
# =============================================================================

fig, ax = plt.subplots(figsize=(8, 5))

razoes = [p/n for p, n in zip(ps, ns)]
cores  = [COR_NEG if g <= 0 else COR_POS for g in gaps]

ax.scatter(razoes, gaps, c=cores, s=70,
           edgecolors='white', linewidths=0.5, zorder=3)
ax.axhline(0, color='black', linewidth=0.8, linestyle='-', zorder=2)
ax.axhline(sum(gaps)/len(gaps), color='#FF9800', linewidth=1.5,
           linestyle='--', zorder=2, label=f'Gap médio: {sum(gaps)/len(gaps):.2f}%')

# Anotações das instâncias com gap extremo
for i, (r, g, inst) in enumerate(zip(razoes, gaps, instancias)):
    if abs(g) > 5:
        ax.annotate(f'pmed{inst}', (r, g),
                    textcoords='offset points', xytext=(5, 5),
                    fontsize=8, color='#333333')

patch_pos = mpatches.Patch(color=COR_POS, label='Gap positivo')
patch_neg = mpatches.Patch(color=COR_NEG, label='Gap negativo')
ax.legend(handles=[patch_pos, patch_neg,
          plt.Line2D([0],[0], color='#FF9800', lw=1.5, linestyle='--',
                     label=f'Gap médio: {sum(gaps)/len(gaps):.2f}%')],
          fontsize=9)

ax.set_xlabel('Razão p/n (densidade de facilidades)')
ax.set_ylabel('Gap (%)')
ax.set_title('Gap (%) × razão p/n\n(quanto maior p/n, mais facilidades relativas ao problema)')

plt.tight_layout()
plt.savefig('graficos/05_gap_vs_razao_pn.png')
plt.close()
print("Gráfico 5 salvo: graficos/05_gap_vs_razao_pn.png")

# =============================================================================
# GRÁFICO 6 — Distribuição dos Gaps (histograma)
# =============================================================================

fig, ax = plt.subplots(figsize=(8, 5))

n_bins = 12
counts, bins, patches = ax.hist(gaps, bins=n_bins, edgecolor='white',
                                 linewidth=0.8, zorder=3)

# Colorir barras: verde se <= 0, vermelho se > 0
for patch, left in zip(patches, bins[:-1]):
    patch.set_facecolor(COR_NEG if left <= 0 else COR_POS)
    patch.set_alpha(0.85)

ax.axvline(0, color='black', linewidth=1, linestyle='-', zorder=4)
ax.axvline(sum(gaps)/len(gaps), color='#FF9800', linewidth=1.5,
           linestyle='--', zorder=4,
           label=f'Média: {sum(gaps)/len(gaps):.2f}%')

gaps_pos = [g for g in gaps if g > 0]
gaps_neg = [g for g in gaps if g <= 0]
ax.text(0.97, 0.95,
        f'Acima do ótimo: {len(gaps_pos)} instâncias\n'
        f'Abaixo/igual:   {len(gaps_neg)} instâncias\n'
        f'Gap máx: {max(gaps):.2f}%\n'
        f'Gap mín: {min(gaps):.2f}%',
        transform=ax.transAxes, fontsize=9, va='top', ha='right',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

ax.set_xlabel('Gap (%)')
ax.set_ylabel('Número de instâncias')
ax.set_title('Distribuição dos gaps da heurística Greedy Addition\n(40 instâncias da OR-Library)')
ax.legend(fontsize=9)

plt.tight_layout()
plt.savefig('graficos/06_distribuicao_gaps.png')
plt.close()
print("Gráfico 6 salvo: graficos/06_distribuicao_gaps.png")

# =============================================================================
# GRÁFICO 7 — Gap médio por grupo de instâncias (agrupado por n)
# =============================================================================

fig, ax = plt.subplots(figsize=(8, 5))

grupos = {}
for r in resultados:
    inst, n, p, ot, heur, gap, tempo = r
    grupos.setdefault(n, []).append(gap)

ns_grupos   = sorted(grupos.keys())
medias      = [sum(grupos[n])/len(grupos[n]) for n in ns_grupos]
desvios     = [np.std(grupos[n]) for n in ns_grupos]
rotulos     = [f'n={n}\n({len(grupos[n])} inst.)' for n in ns_grupos]

cores_grupo = [COR_NEG if m <= 0 else COR_POS for m in medias]

bars = ax.bar(rotulos, medias, color=cores_grupo, edgecolor='white',
              linewidth=0.5, zorder=3, alpha=0.85, yerr=desvios,
              capsize=4, error_kw={'linewidth': 1.2, 'color': '#555'})

ax.axhline(0, color='black', linewidth=0.8, linestyle='-', zorder=4)
ax.axhline(sum(gaps)/len(gaps), color='#FF9800', linewidth=1.5,
           linestyle='--', zorder=4,
           label=f'Gap médio geral: {sum(gaps)/len(gaps):.2f}%')

# Rótulo do valor em cada barra
for bar, m in zip(bars, medias):
    ax.text(bar.get_x() + bar.get_width()/2,
            m + (0.15 if m >= 0 else -0.35),
            f'{m:.2f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.set_xlabel('Grupo de instâncias (por tamanho n)')
ax.set_ylabel('Gap médio (%)')
ax.set_title('Gap médio por grupo de instâncias\n(barras de erro = desvio padrão)')
ax.legend(fontsize=9)

plt.tight_layout()
plt.savefig('graficos/07_gap_medio_por_grupo.png')
plt.close()
print("Gráfico 7 salvo: graficos/07_gap_medio_por_grupo.png")

# =============================================================================
# GRÁFICO 8 — Tempo médio por grupo de instâncias
# =============================================================================

fig, ax = plt.subplots(figsize=(8, 5))

grupos_tempo = {}
for r in resultados:
    inst, n, p, ot, heur, gap, tempo = r
    grupos_tempo.setdefault(n, []).append(tempo)

medias_tempo = [sum(grupos_tempo[n])/len(grupos_tempo[n]) for n in ns_grupos]
desvios_tempo= [np.std(grupos_tempo[n]) for n in ns_grupos]

bars = ax.bar(rotulos, medias_tempo, color=COR_TEMPO, edgecolor='white',
              linewidth=0.5, zorder=3, alpha=0.85,
              yerr=desvios_tempo, capsize=4,
              error_kw={'linewidth': 1.2, 'color': '#555'})

for bar, m in zip(bars, medias_tempo):
    ax.text(bar.get_x() + bar.get_width()/2, m + 0.1,
            f'{m:.2f}s', ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.set_xlabel('Grupo de instâncias (por tamanho n)')
ax.set_ylabel('Tempo médio (segundos)')
ax.set_title('Tempo médio de execução por grupo de instâncias\n(barras de erro = desvio padrão)')

plt.tight_layout()
plt.savefig('graficos/08_tempo_medio_por_grupo.png')
plt.close()
print("Gráfico 8 salvo: graficos/08_tempo_medio_por_grupo.png")

# =============================================================================
# RESUMO FINAL
# =============================================================================

print()
print("=" * 55)
print("  Todos os gráficos foram gerados na pasta 'graficos/'")
print("=" * 55)
print(f"  01_gap_por_instancia.png    — Gap (%) por instância")
print(f"  02_heuristica_vs_otimo.png  — Heurística vs Ótimo")
print(f"  03_tempo_por_instancia.png  — Tempo por instância")
print(f"  04_tempo_vs_n.png           — Tempo × tamanho n")
print(f"  05_gap_vs_razao_pn.png      — Gap × razão p/n")
print(f"  06_distribuicao_gaps.png    — Histograma dos gaps")
print(f"  07_gap_medio_por_grupo.png  — Gap médio por grupo")
print(f"  08_tempo_medio_por_grupo.png— Tempo médio por grupo")
print("=" * 55)
