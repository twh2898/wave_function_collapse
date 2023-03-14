#!/usr/bin/env python3

from random import randint, choice

letter = 'ABCDEFGHIJ'

SHOW_SOLVE = True


class Cell:
    value: int | None = None

    def __init__(self, r, c):
        self.r = r
        self.c = c
        self.options = list(range(1, 10))

    def __repr__(self):
        if SHOW_SOLVE:
            if self.value:
                return str(self.value)
            else:
                return '?'
        else:
            if self.value:
                return '*'
            else:
                return str(len(self.options))

    def fill(self):
        assert len(self.options) > 0
        self.value = choice(self.options)
        self.options.clear()

    def remove_option(self, option):
        if option in self.options:
            self.options.remove(option)

    def entropy(self):
        return len(self.options)

    def complete(self):
        return self.entropy() == 0


class Sudoku:
    def __init__(self):
        self._cells = [[Cell(r, c) for c in range(9)] for r in range(9)]

    def __repr__(self):
        lines = ''
        for r in range(9):
            for c in range(9):
                cell = self.get_cell(r, c)
                lines += ' {}'.format(cell)
            lines += '\n'
        return lines

    def get_cell(self, r, c):
        assert 0 <= r <= 9
        assert 0 <= c <= 9
        return self._cells[r][c]


def collapse(target: Cell, sudoku: Sudoku):
    for c in range(9):
        if c == target.c:
            continue
        cell = sudoku.get_cell(target.r, c)
        cell.remove_option(target.value)

    for r in range(9):
        if r == target.r:
            continue
        cell = sudoku.get_cell(r, target.c)
        cell.remove_option(target.value)

    r_block = target.r % 3
    c_block = target.c % 3

    for r in range(3):
        r += r_block * 3
        for c in range(3):
            c += c_block * 3

            if r == target.r and c == target.c:
                continue

            cell = sudoku.get_cell(r, c)
            cell.remove_option(target.value)


def solve(sudoku: Sudoku):
    cells = []
    for row in sudoku._cells:
        cells += row

    cell = choice(cells)
    cells.remove(cell)
    cell.fill()
    collapse(cell, sudoku)
    for cell in cells:
        assert len(cell.options) > 0
        if len(cell.options) == 1:
            cell.value = cell.options[0]
            cell.options.clear()
    cells = list(filter(lambda c: not c.complete(), cells))

    while cells:
        cells.sort(key=lambda c: c.entropy())
        low_entropy = cells[0].entropy()
        sub_cells = list(filter(lambda c: c.entropy() == low_entropy, cells))
        cell = choice(sub_cells)
        cells.remove(cell)
        cell.fill()
        collapse(cell, sudoku)
        for cell in cells:
            assert len(cell.options) > 0
            if len(cell.options) == 1:
                cell.value = cell.options[0]
                cell.options.clear()
        cells = list(filter(lambda c: not c.complete(), cells))


def test(sudoku: Sudoku):
    for row in sudoku._cells:
        for cell in row:
            assert cell.value is not None, f'Cell {cell.r} {cell.c} is None'
            assert cell.entropy() == 0

    for r in range(9):
        r_vals = [sudoku.get_cell(r, c).value for c in range(9)]
        for i in range(1, 10):
            assert i in r_vals

    for c in range(9):
        c_vals = [sudoku.get_cell(r, c).value for r in range(9)]
        for i in range(1, 10):
            assert i in c_vals

    for r_block in range(3):
        for c_block in range(3):
            block_cells = []

            for r in range(3):
                r += r_block * 3
                for c in range(3):
                    c += c_block * 3

                    cell = sudoku.get_cell(r, c)
                    block_cells.append(cell.value)

            for i in range(1, 10):
                assert i in block_cells


if __name__ == '__main__':
    s = Sudoku()
    solve(s)
    print(s)
    test(s)
