#!/usr/bin/env python3

import sys
import colorama
from wfc import Grid, propagate, Tile, Cell, collapse
from typing import TextIO


def clean_hex(n: int):
    """Return a 2 character hex string for integer n with space padding."""
    return '{:2s}'.format(hex(n)[2:])


def load_rules():
    # Water, Beach, Grass, Mountain (gray)
    pass


def load_grid(w: int, h: int):
    """Create a grid of width w and height h."""
    cells = {}
    for y in range(h):
        for x in range(w):
            options = [t for t in Tile]
            cell = Cell(x, y, options)
            cells[(x, y)] = cell
    return Grid(w, h, cells)


def init_grid(grid: Grid):
    """Set the borders of grid to water and add a stone to the center."""
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


def print_grid(grid: Grid, f: TextIO | None = sys.stdout):
    """Print grid to a file stream."""
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


def print_grids(grids: list[Grid], h: int, f: TextIO | None = sys.stdout):
    """Print multiple grids to a file stream."""
    for y in range(h):
        for g in grids:
            for x in range(g.w):
                cell = g[(x, y)]
                print(cmap[cell.value] + "██" +
                      colorama.Fore.RESET, end="", file=f)
            print('  ', end='', file=f)
        print(file=f)


def main_multi(w, h, rules):
    """Generate multiple grids."""
    for _ in range(5):
        grids = []
        for _ in range(3):
            grid = load_grid(w, h)
            init_grid(grid)

            while not grid.is_solved():
                collapse(grid, rules)

            grids.append(grid)

        print()
        print_grids(grids, h)


def main(w, h, rules, debug=False, f=None):
    """Generate a single grid."""
    rules = load_rules()

    grid = load_grid(w, h)
    init_grid(grid)
    if debug:
        if f:
            f.write('0\n')
        print_grid(grid, f)
        print_grid(grid)

    i = 1
    while not grid.is_solved():
        collapse(grid, rules)
        if debug:
            if f:
                f.write(str(i) + '\n')
            print_grid(grid, f)
            print_grid(grid)
        i += 1

    print_grid(grid)


if __name__ == '__main__':
    for i in range(16):
        s = Tile.whoami(i)
        print(clean_hex(i), '=', s)

    # rules = rules_from_img(img)
    rules = load_rules()

    use_multi = True

    if use_multi:
        main_multi(16, 16, rules)

    else:
        with open('debug', 'w') as f:
            main(16, 16, rules, debug=True, f=f)
