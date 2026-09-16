"""
Visualiza o estado inicial e final da simulacao de Ant Colony Clustering (ACC)
definida em ant-colony-2.py.

Requisitos:
    pip install matplotlib numpy

Este script deve ficar na MESMA pasta que "ant-colony-2.py" (e, se voce tiver
um dataset proprio, tambem um arquivo "dataset.txt" com linhas no formato:
    x  y  id
separadas por espaco). Se "dataset.txt" nao existir, um dataset sintetico e
gerado automaticamente apenas para fins de demonstracao.
"""

import os
import sys
import random
import importlib.util

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches


# ----------------------------------------------------------------------
# Parametros da simulacao (ajuste livremente)
# ----------------------------------------------------------------------
WIDTH, HEIGHT = 64, 64        # tamanho da grade
NUM_ANTS = 15                 # numero de formigas
RADIUS = 1                    # raio de percepcao da formiga
ITERATIONS = 10000000          # numero de iteracoes
ALPHA = 0.6                  # alpha (escala de similaridade)
K1 = 0.1                      # k1 (constante de "pegar" item)
K2 = 0.                    # k2 (constante de "largar" item)
DATASET_PATH = "./dataset.txt"
MODULE_PATH = "./ant-colony-2.py"


# ----------------------------------------------------------------------
# 1. Carrega as classes Grid/Ant/Item/Cell de ant-colony-2.py
#    (importlib e necessario pois o nome do arquivo contem hifen)
# ----------------------------------------------------------------------
spec = importlib.util.spec_from_file_location("ant_colony_2", MODULE_PATH)
ant_colony_2 = importlib.util.module_from_spec(spec)
sys.modules["ant_colony_2"] = ant_colony_2
spec.loader.exec_module(ant_colony_2)
Grid = ant_colony_2.Grid

# ----------------------------------------------------------------------
# 3. Funcoes auxiliares para converter a grade em imagem colorida
# ----------------------------------------------------------------------
def grid_to_id_matrix(grid):
    """Matriz numpy com o id do item em cada celula (-1 = celula vazia)."""
    arr = np.full((grid.width, grid.height), -1, dtype=int)
    for x in range(grid.width):
        for y in range(grid.height):
            cell = grid.matrix[x][y]
            if cell.has_item():
                arr[x, y] = cell.item.id
    return arr


def build_discrete_colormap(all_ids):
    """Colormap discreto: indice 0 = celula vazia, 1..N = um id cada, cores bem distintas."""
    ids_sorted = sorted(all_ids)
    n = len(ids_sorted)
    base_cmap = plt.get_cmap("nipy_spectral", max(n, 1))

    colors = ["#e8e8e8"]  # celula vazia
    colors += [mcolors.to_hex(base_cmap(i)) for i in range(n)]

    cmap = mcolors.ListedColormap(colors)
    bounds = np.arange(-0.5, len(colors) + 0.5, 1)
    norm = mcolors.BoundaryNorm(bounds, cmap.N)

    id_to_index = {item_id: idx + 1 for idx, item_id in enumerate(ids_sorted)}
    return cmap, norm, id_to_index


def remap_with_index(arr, id_to_index):
    remapped = np.zeros_like(arr)
    for item_id, idx in id_to_index.items():
        remapped[arr == item_id] = idx
    return remapped


def plot_state(ax, arr, cmap, norm, title):
    ax.imshow(arr, cmap=cmap, norm=norm, interpolation="nearest")
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xticks([])
    ax.set_yticks([])


def main():
    grid = Grid(width=WIDTH, height=HEIGHT, alpha=ALPHA, k1=K1, k2=K2)
    grid.initialize_matriz()
    grid.create_items(DATASET_PATH)
    grid.populate_ants(NUM_ANTS, RADIUS)

    arr_before = grid_to_id_matrix(grid)

    # Observacao: reproduzimos o loop principal de Grid.run(), mas sem a fase
    # final de limpeza ("while self.ants != []"), pois essa fase pode ficar
    # presa indefinidamente se alguma formiga nunca soltar o item que carrega.
    for _ in range(ITERATIONS):
        for ant in grid.ants:
            grid.round(ant)

    arr_after = grid_to_id_matrix(grid)

    all_ids = (set(arr_before.flatten().tolist()) | set(arr_after.flatten().tolist())) - {-1}
    cmap, norm, id_to_index = build_discrete_colormap(all_ids)
    remapped_before = remap_with_index(arr_before, id_to_index)
    remapped_after = remap_with_index(arr_after, id_to_index)

    fig, axes = plt.subplots(1, 2, figsize=(13, 6.5))
    plot_state(axes[0], remapped_before, cmap, norm, "Estado Inicial")
    plot_state(axes[1], remapped_after, cmap, norm, "Estado Final")

    if 0 < len(all_ids) <= 20:
        handles = [
            mpatches.Patch(color=cmap(id_to_index[i]), label=f"id {i}")
            for i in sorted(all_ids)
        ]
        fig.legend(
            handles=handles, loc="lower center", ncol=min(10, len(handles)),
            bbox_to_anchor=(0.5, 0.08), fontsize=9, frameon=False,
        )

    params_text = (
        f"Grid: {WIDTH} x {HEIGHT}   |   Formigas: {NUM_ANTS}   |   "
        f"Iteracoes: {ITERATIONS}   |   Itens: {int((arr_before >= 0).sum())}\n"
        f"alpha = {ALPHA}   |   k1 = {K1}   |   k2 = {K2}   |   raio = {RADIUS}"
    )
    fig.suptitle("Simulacao de Ant Colony Clustering (ACC)", fontsize=15, fontweight="bold")
    fig.text(0.5, 0.01, params_text, ha="center", fontsize=10)

    plt.tight_layout(rect=[0, 0.10, 1, 0.93])
    plt.savefig("acc_before_after.png", dpi=150)
    plt.show()
    print('Figura salva em "acc_before_after.png"')


if __name__ == "__main__":
    main()