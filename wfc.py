#!/usr/bin/env python3

import sys
import colorama
from random import randint, choice

from enum import Enum, auto
from dataclasses import dataclass


def clean_hex(n: int):
    return '{:2s}'.format(hex(n)[2:])


class Tile(Enum):
    Water = 1
    Sand = 2
    Grass = 4
    Stone = 8

    @classmethod
    def from_value(cls, value):
        match value:
            case 1:
                return cls.Water
            case 2:
                return cls.Sand
            case 4:
                return cls.Grass
            case 8:
                return cls.Stone

    @classmethod
    def whoami(cls, n):
        assert 0 <= n < 16, 'N must be 0 to 16'
        res = []
        if n & 1:
            res.append(cls.Water)
        if n & 2:
            res.append(cls.Sand)
        if n & 4:
            res.append(cls.Grass)
        if n & 8:
            res.append(cls.Stone)
        return res


@dataclass
class Cell:
    x: int
    y: int
    options: list
    value: Tile | None = None

    def remove(self, *options):
        for option in options:
            if option in self.options:
                self.options.remove(option)
        assert len(self.options) > 0, 'Cell ran out of options'

    def is_solved(self):
        return self.value is not None

    def entropy(self, grid: 'Grid'):
        if self.is_solved():
            return -1

        r = max(self.x, grid.w - self.x) ** 2 \
            + max(self.y, grid.h - self.y) ** 2
        return len(self.options) ** r


@dataclass
class Grid:
    w: int
    h: int
    cells: dict[tuple[int, int], Cell]

    def is_solved(self):
        for cell in self.cells.values():
            if not cell.is_solved():
                return False
        return True

    def __getitem__(self, key: tuple[int, int]):
        return self.cells.__getitem__(key)

    def __iter__(self):
        return iter(self.cells.values())


def load_rules():
    # Water, Beach, Grass, Mountain (gray)
    pass


def rules_from_img(img):
    pass


def get_min_entropy(grid: Grid):
    def entropy(cell: Cell):
        return cell.entropy(grid)

    flat = list(grid)
    flat.sort(key=entropy)

    flat = list(filter(lambda c: not c.is_solved(), flat))
    assert len(flat) > 0, 'No cells left'

    min_e = entropy(flat[0])
    flat = list(filter(lambda c: entropy(c) == min_e, flat))
    assert len(flat) > 0, 'No cells left'

    return choice(flat)


def cell_neighbors(cell: Cell, grid: Grid) -> list[Cell]:
    cells = []

    if cell.x > 0:
        cells.append(grid[(cell.x - 1, cell.y)])

    if cell.x < grid.w - 1:
        cells.append(grid[(cell.x + 1, cell.y)])

    if cell.y > 0:
        cells.append(grid[(cell.x, cell.y - 1)])

    if cell.y < grid.h - 1:
        cells.append(grid[(cell.x, cell.y + 1)])

    assert len(cells) > 0, 'No neighbors found'

    return cells


def propagate(cell: Cell, grid: Grid, rules):
    if len(cell.options) == 1:
        cell.value = cell.options[0]
        cell.options.clear()

    for neighbor in cell_neighbors(cell, grid):
        if neighbor.is_solved():
            continue

        assert len(neighbor.options) > 0, 'Cell has no options'
        assert len(neighbor.options) > 1, 'Cell should already be solved'

        neighbor_before = len(neighbor.options)

        match cell.value:
            case Tile.Water:
                neighbor.remove(Tile.Grass, Tile.Stone)
            case Tile.Sand:
                neighbor.remove(Tile.Stone)
            case Tile.Grass:
                neighbor.remove(Tile.Water)
            case Tile.Stone:
                neighbor.remove(Tile.Water, Tile.Sand)
            case None:
                if Tile.Grass not in cell.options:
                    neighbor.remove(Tile.Stone)
                if Tile.Sand not in cell.options:
                    neighbor.remove(Tile.Water)
                assert len(neighbor.options) > 0, 'Removed too many options'

        neighbor_after = len(neighbor.options)
        neighbor_updated = neighbor_after != neighbor_before

        if neighbor_updated:
            propagate(neighbor, grid, rules)


def collapse_cell(cell: Cell):
    assert not cell.is_solved(), 'Cell is already solved'
    assert len(cell.options) > 0, 'Cell has no options'
    cell.value = choice(cell.options)
    cell.options.clear()


def collapse(grid: Grid, rules):
    cell = get_min_entropy(grid)
    collapse_cell(cell)
    propagate(cell, grid, rules)


def collapse_tmp(grid: Grid):
    for cell in grid:
        if not is_cell_solved(cell):
            cell.value = Tile.Sand


def is_cell_solved(cell: Cell):
    return cell.is_solved()


def is_solved(grid: Grid):
    return grid.is_solved()


def load_grid(w: int, h: int):
    cells = {}
    for y in range(h):
        for x in range(w):
            options = [t for t in Tile]
            cell = Cell(x, y, options)
            cells[(x, y)] = cell
    return Grid(w, h, cells)


def init_grid(grid: Grid):
    for x in range(grid.w):
        cell = grid[(x, 0)]
        cell.value = Tile.Water
        cell.options.clear()
        propagate(cell, grid, None)

        cell = grid[(x, grid.h-1)]
        cell.value = Tile.Water
        cell.options.clear()
        propagate(cell, grid, None)

    for y in range(grid.h):
        cell = grid[(0, y)]
        cell.value = Tile.Water
        cell.options.clear()
        propagate(cell, grid, None)

        cell = grid[(grid.w-1, y)]
        cell.value = Tile.Water
        cell.options.clear()
        propagate(cell, grid, None)

    cell = grid[(grid.w//2, grid.h//2)]
    cell.value = Tile.Stone
    cell.options.clear()
    propagate(cell, grid, None)


cmap = {
    Tile.Water: colorama.Fore.CYAN,
    Tile.Sand: colorama.Fore.YELLOW,
    Tile.Grass: colorama.Fore.GREEN,
    Tile.Stone: colorama.Fore.BLACK,
    None: colorama.Fore.RED,
}


def debug_grid(grid: Grid, f=None):
    for y in range(grid.h):
        for x in range(grid.w):
            cell = grid[(x, y)]
            if cell.is_solved():
                print(cmap[cell.value] + "██" +
                      colorama.Fore.RESET, end="", file=f)
            else:
                mask = 0
                for v in cell.options:
                    mask |= v.value
                print(clean_hex(mask) + colorama.Fore.RESET, end="", file=f)
        print(file=f)
    print(file=f)


def print_grid(grid: Grid):
    for y in range(grid.h):
        for x in range(grid.w):
            cell = grid[(x, y)]
            print(cmap[cell.value] + "██" + colorama.Fore.RESET, end="")
        print()


def print_grids(grids: list[Grid], h: int):
    for y in range(h):
        for g in grids:
            for x in range(g.w):
                cell = g[(x, y)]
                print(cmap[cell.value] + "██" + colorama.Fore.RESET, end="")
            print('  ', end='')
        print()


def main_multi(w, h, rules):
    for _ in range(5):
        grids = []
        for _ in range(3):
            grid = load_grid(w, h)
            init_grid(grid)

            while not is_solved(grid):
                collapse(grid, rules)

            grids.append(grid)

        print()
        print_grids(grids, h)


def main(w, h, rules, debug=False, f=None):
    # rules = rules_from_img(img)
    rules = load_rules()

    grid = load_grid(w, h)
    init_grid(grid)
    if debug:
        if f:
            f.write('0\n')
        debug_grid(grid, f)
        debug_grid(grid, sys.stdout)

    i = 1
    while not is_solved(grid):
        collapse(grid, rules)
        if debug:
            if f:
                f.write(str(i) + '\n')
            debug_grid(grid, f)
            debug_grid(grid, sys.stdout)
        i += 1
    # TODO: Write grid for each step to file for later review
    # Show in pyplot or print to console with clear before next draw

    print_grid(grid)


if __name__ == '__main__':
    # for i in range(16):
    #     s = Tile.whoami(i)
    #     print(clean_hex(i), '=', s)

    # rules = rules_from_img(img)
    rules = load_rules()

    main_multi(24, 24, rules)
    # with open('debug', 'w') as f:
    #     main(16, 16, rules, debug=True, f=f)
