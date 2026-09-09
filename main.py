import random

class Item:

    def __init__(self):
        pass


class Ant:
    def __init__(self, radius=1, position=None):
        self.radius = radius        
        self.moves = ['L', 'R', 'U', 'D']
        self.is_free = True        
        self.carried_item = None    
        self.position = position    

    def is_carrying_item(self):
        return self.carried_item is not None

    def pick_item(self, item):
        self.carried_item = item
        self.is_free = False

    def drop_item(self):
        item = self.carried_item
        self.carried_item = None
        self.is_free = True
        return item

    def next_position(self, width, height):

        m = random.choice(self.moves)

        x, y = self.position

        match m:
            case 'L':
                x -= 1
            case 'R':
                x += 1
            case 'U':
                y -= 1
            case 'D':
                y += 1
            case _:
                pass

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

    def __init__(self, width=50, height=50, radius=1):
        self.width = width
        self.height = height
        self.radius = radius
        self.matrix = []
        self.ants = []

    def initialize_matriz(self):
        self.matrix = []
        for i in range(self.width):
            row = []
            for j in range(self.height):
                row.append(Cell())
            self.matrix.append(row)

    def populate_ants(self, num_ants, radius):
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

    def populate_items(self, num_itens):
        i = 0
        while i < num_itens:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)

            cell = self.matrix[x][y]

            if not cell.has_item():
                cell.set_item(Item())
                i += 1

    def show_matrix_itens(self):
        for i in range(self.width):
            for j in range(self.height):
                cell = self.matrix[i][j]
                print("1" if cell.has_item() else " ", end=" ")
            print()

    def local_density(self, x, y, radius):
        
        count_items = 0
        count_cells = 0

        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx == 0 and dy == 0:
                    continue
                nx = (x + dx) % self.width
                ny = (y + dy) % self.height
                count_cells += 1
                if self.matrix[nx][ny].has_item():
                    count_items += 1

        return count_items / count_cells

    def try_pick_up(self, ant, cell):
        f = self.local_density(ant.position[0], ant.position[1], ant.radius)
        prob = 1 - f
        if random.random()< prob:
            item = cell.item
            cell.clear_item()
            ant.pick_item(item)

    def try_drop(self, ant, cell):
        f = self.local_density(ant.position[0], ant.position[1], ant.radius)
        prob = f
        if  random.random() < prob:
            item = ant.drop_item()
            cell.set_item(item)

    def round(self):
        for ant in self.ants:
            x, y = ant.position
            current_cell = self.matrix[x][y]

            new_x, new_y = ant.next_position(self.width, self.height)
            target_cell = self.matrix[new_x][new_y]

            if not target_cell.has_ant():
                current_cell.clear_ant()
                ant.position = (new_x, new_y)
                target_cell.set_ant(ant)
                current_cell = target_cell

            if ant.is_free and current_cell.has_item():
                self.try_pick_up(ant, current_cell)
            elif not ant.is_free and not current_cell.has_item():
                self.try_drop(ant, current_cell)

    def run(self, iterations):
        for _ in range(iterations):
            self.round()


if __name__ == "__main__":
    WIDTH, HEIGHT = 50, 50
    NUM_ITEMS = 600
    NUM_ANTS = 15
    RADIUS = 1
    ITERATIONS = 100000

    grid = Grid(width=WIDTH, height=HEIGHT)
    grid.initialize_matriz()
    grid.populate_items(NUM_ITEMS)
    grid.populate_ants(NUM_ANTS, RADIUS)

    print("ESTADO INICIAL: \n")
    grid.show_matrix_itens()

    grid.run(ITERATIONS)

    print(f"\nESTADO FINAL:\n")
    grid.show_matrix_itens()

    j = 0 
    for i in grid.ants: 
        print(f"{(j, i.is_free)} \n")
        j+=1

