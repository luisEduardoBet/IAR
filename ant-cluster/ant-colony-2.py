import random
import matplotlib.pyplot as plt
import numpy as np
from math import sqrt
import matplotlib.colors as mcolors

class Item:
    def __init__(self, x, y, id):
        self.x = x
        self.y = y
        self.id = id


class Ant:
    def __init__(self, radius=1, position=None):
        self.radius = radius
        self.moves = ['L', 'R', 'U', 'D']
        self.is_free = True
        self.item = None
        self.position = position

    def is_carrying_item(self):
        return self.item is not None

    def pick_item(self, item):
        self.item = item
        self.is_free = False

    def drop_item(self):
        item = self.item
        self.item = None
        self.is_free = True
        return item

    def next_position(self, width, height):
        m = random.choice(self.moves)
        x, y = self.position
        if m == 'L':
            x -= 1
        elif m == 'R':
            x += 1
        elif m == 'U':
            y -= 1
        elif m == 'D':
            y += 1
        x %= width
        y %= height
        return (x, y)


class Cell:
    def __init__(self):
        self.item = None
        self.ant = None

    def set_item(self, item):
        self.item = item

    def clear_item(self):
        self.item = None

    def set_ant(self, ant):
        self.ant = ant

    def clear_ant(self):
        self.ant = None

    def has_ant(self):
        return self.ant is not None

    def has_item(self):
        return self.item is not None


class Grid:
    def __init__(self, width=64, height=64, alpha=0.6, k1=0.1, k2=0.1):
        self.width = width
        self.height = height
        self.matrix = []
        self.ants = []  
        self.alpha = alpha
        self.k1 = k1
        self.k2 = k2

    def initialize_matriz(self):
        for i in range(self.width):
            row = []
            for j in range(self.height):
                row.append(Cell())
            self.matrix.append(row)

    def populate_ants(self, num_ants = 15, radius=1):
        i = 0
        while i < num_ants:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            cell = self.matrix[x][y]
            if not cell.has_ant():
                ant = Ant(radius=radius, position=(x, y))
                self.ants.append(ant)
                cell.set_ant(ant)
                i += 1

    def create_items(self, path=""):
        f = open(path, "r")
        lx, ly = None, None
        gx, gy = None, None
        lista = []

        for i in f:
            splitted = tuple(map(float, i.split()))
            if lx is None or splitted[0] < lx:
                lx = splitted[0]
            if ly is None or splitted[1] < ly:
                ly = splitted[1]
            if gx is None or splitted[0] > gx:
                gx = splitted[0]
            if gy is None or splitted[1] > gy:
                gy = splitted[1]
            lista.append(splitted)

        for i in lista:
            x = self.__normalization(lx, gx, i[0])
            y = self.__normalization(ly, gy, i[1])
            id = int(i[2])
            self.__populate_itens(Item(x, y, id))

    def __populate_itens(self, item):
        cond = True
        while cond:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            cell = self.matrix[x][y]
            if not cell.has_item():
                cell.set_item(item)
                cond = False

    def __normalization(self, minv, maxv, value):
        n = (value - minv) / (maxv - minv)
        return n
    
    def show_matrix_itens(self):
        for i in range(self.width):
            for j in range(self.height):
                cell = self.matrix[i][j]
                print(cell.item.id if cell.has_item() else " ", end=" ")
            print()


    def local_density(self, item, x, y, radius):

        similarity = 0.0
        s = 2 * radius + 1

        for rx in range(-radius, radius + 1):
            for ry in range(-radius, radius + 1):
                if rx == 0 and ry == 0:
                    continue

                nx = (x + rx) % self.width
                ny = (y + ry) % self.height
                cell = self.matrix[nx][ny]

                if cell.has_item():
                    dist = sqrt((item.x - cell.item.x) ** 2 + (item.y - cell.item.y) ** 2)
                    term = 1.0 - dist / self.alpha
                    if term > 0:
                        similarity += term

        f = similarity / (s*s)
        return f

    def try_pick_up(self, ant, cell):
        f = self.local_density(cell.item, ant.position[0], ant.position[1], ant.radius)
        prob = (self.k1 / (self.k1 + f)) ** 2
        if random.random() <= prob:
            item = cell.item
            cell.clear_item()
            ant.pick_item(item)

    def try_drop(self, ant, cell):
        f = self.local_density(ant.item, ant.position[0], ant.position[1], ant.radius)
        if f >= self.k2:
            prob = 1
        else:
            prob = 2 * f

        if random.random() < prob:
            item = ant.drop_item()
            cell.set_item(item)

    def shift(self, ant):
        x, y = ant.position
        current_cell = self.matrix[x][y]

        new_x, new_y = ant.next_position(self.width, self.height)
        next_cell = self.matrix[new_x][new_y]

        if not next_cell.has_ant():
            current_cell.clear_ant()
            ant.position = (new_x, new_y)
            next_cell.set_ant(ant)
            current_cell = next_cell

        if ant.is_free and current_cell.has_item():
            self.try_pick_up(ant, current_cell)
        elif not ant.is_free and not current_cell.has_item():
            self.try_drop(ant, current_cell)

    def run(self, iterations):
        for i in range(iterations):
            for j in self.ants: 
                self.shift(j)

        i = 0
        while self.ants != []: 
            ant = self.ants[i]
            if ant.is_free: 
                self.ants.remove(ant)
            else: 
                self.shift(ant)

cores_hex = [
    '#ffffff', # 0: Branco
    '#e6194b', # 1: Vermelho
    '#3cb44b', # 2: Verde
    '#ffe119', # 3: Amarelo
    '#4363d8', # 4: Azul
    '#f58231', # 5: Laranja
    '#911eb4', # 6: Roxo
    '#46f0f0', # 7: Ciano
    '#f032e6', # 8: Magenta
    '#bcfd4c', # 9: Lima
    '#fabebe', # 10: Rosa
    '#008080', # 11: Verde-petróleo
    '#e6beff', # 12: Lavanda
    '#9a6324', # 13: Marrom
    '#800000', # 14: Vinho
    '#000075'  # 15: Azul-marinho
]





def plotting(grid, path, title, title2, title3):
    fig, ax = plt.subplots()
    plt.suptitle(title, x=0.512, y=1.01, fontsize=12, ha='center')
    plt.title( title2,fontsize=10, y=1.055, color='#444', ha='center')
    plt.gcf().text(0.512, 0.9, title3, ha='center', fontsize=8, color='#666')

   
    meu_cmap = mcolors.ListedColormap(cores_hex)
    bounds = np.arange(17) - 0.5
    norm = mcolors.BoundaryNorm(bounds, meu_cmap.N)
    
    arr = np.full((grid.width, grid.height), -1, dtype=int)
    for x in range(grid.width):
        for y in range(grid.height):
            cell = grid.matrix[x][y]
            if cell.has_item():
                arr[x, y] = cell.item.id

    ax.imshow(arr, cmap=meu_cmap, norm=norm)
    
    ax.set_xticks(np.arange(-0.5, grid.height, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, grid.width, 1), minor=True)
    
    ax.grid(which='minor', color='black', linestyle='-', linewidth=0.5)
    
    ax.tick_params(which='both', bottom=False, left=False, labelbottom=False, labelleft=False)

    plt.savefig(path, bbox_inches='tight', dpi=300)
    plt.close()

grid = Grid()

if __name__ == "__main__":
    WIDTH, HEIGHT = 50, 50
    #NUM_ITEMS = 600
    NUM_ANTS = 15
    RADIUS = 1
    ITERATIONS = 2000000
    ALPHA=0.6 
    K1=0.1 
    K2=0.1

    grid = Grid(width=WIDTH, height=HEIGHT)
    desc2 = f"Grid: {WIDTH}X{HEIGHT}| ANTS: {NUM_ANTS}; RADIUS: {RADIUS} | ITER: {ITERATIONS}"
    desc3 = f"ALPHA: {ALPHA} | K1: {K1} | K2: {K2}"

    grid.initialize_matriz()
    grid.create_items("./dataset-15.txt")
    grid.populate_ants(NUM_ANTS, RADIUS)


    plotting(grid, f"./antes/teste.png", "Estado Inicial", desc2, desc3)

    grid.run(ITERATIONS)

    plotting(grid, f"./depois/teste.png", "Estado Final", desc2, desc3)




    # iteracoes = [10000000, 20000000, 50000000]
    # k1 = [0.1, 0.5,  0.9] 
    # k2 = [0.1, 0.025, 0.05]
    # alpha = [0.6, 0.35, 0.11]

    # k = 0
    # for i in iteracoes: 
    #     j = 0 
    #     while j < 3: 

    #         grid = Grid(width=WIDTH, height=HEIGHT, alpha= alpha[j], k1=k1[j], k2=k2[j])
    #         desc2 = f"Grid: {WIDTH}X{HEIGHT}| ANTS: {NUM_ANTS}; RADIUS: {RADIUS} | ITER: {i}"
    #         desc3 = f"ALPHA: {alpha[j]} | K1: {k1[j]} | K2: {k2[j]}"

    #         grid.initialize_matriz()
    #         grid.create_items("./dataset.txt")
    #         grid.populate_ants(NUM_ANTS, RADIUS)


    #         plotting(grid, f"./antes/teste_{k}.png", "Estado Inicial", desc2, desc3)

    #         grid.run(i)

    #         plotting(grid, f"./depois/teste_{k}.png", "Estado Final", desc2, desc3)
    #         j+=1
    #         k+=1