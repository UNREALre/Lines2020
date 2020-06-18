#! /usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
from os.path import join
from config import PROJECT_ROOT

default_sprite = join(PROJECT_ROOT, 'sprites/grid9x9.jpg')


class Grid:

    """Класс для работы с сеткой на которой происходит вся игра"""

    def __init__(self, sprite=None):
        """Инициализирует игровую сетку"""

        # Сетка в виде списка списокв - пустая матрица
        self.matrix = [[None] * 9 for i in range(9)]

        # image.load возвращает Surface объект
        self.sprite = pygame.image.load(join(PROJECT_ROOT, sprite)) if sprite else pygame.image.load(default_sprite)
        self.width, self.height = self.sprite.get_size()

        scr_width, scr_height = pygame.display.get_surface().get_size()
        self.x_centered = scr_width / 2 - self.width / 2
        self.y_centered = scr_height / 2 - self.height / 2

        self._grid_cell_width = 58
        self._grid_cell_height = 58

    def draw(self, surface):
        """Рисует игровую сетку"""

        surface.blit(self.sprite, (self.x_centered, self.y_centered))

    def add_to_matrix(self, matrix_pos, ball):
        """Добавляет новый шарик в матрицу сетки"""

        self.matrix[matrix_pos[0]][matrix_pos[1]] = ball
        pass

    def delete_from_matrix(self, matrix_pos):
        """Удаляет шарик из матрицы сетки"""

        self.matrix[matrix_pos[0]][matrix_pos[1]] = None

    def move_ball_in_matrix(self, ball, new_matrix_pos):
        """Перемещает шарик в матрице. Получает шарик выделенный и новую его позицию в матрице"""

        self.matrix[new_matrix_pos[0]][new_matrix_pos[1]] = ball
        self.delete_from_matrix((ball.mx_pos_row, ball.mx_pos_col))

    def matrix_pos_to_grid_coords(self, matrix_pos):
        """Получает позиции в матрице сетки - возвращает соответствующие ей координаты на сетке"""

        pos_x = self._grid_cell_width * matrix_pos[1] + self.x_centered
        pos_x += matrix_pos[1] + 5  # поправка на границы ячеек и центровку
        pos_y = self._grid_cell_height * matrix_pos[0] + self.y_centered
        pos_y += matrix_pos[0] + 5

        return pos_x, pos_y

    def update_grid(self, matrix_pos, ball, surface):
        """Добавляет шар на сетку (отрисовка)"""

        self.add_to_matrix(matrix_pos, ball)
        surface.blit(ball.sprite, (ball.pos_x, ball.pos_y))

    def reset(self, surface):
        """Очищает сетку и матрицу"""
        self.matrix = [[None] * 9 for i in range(9)]
        self.draw(surface)

    def get_ball_from_cell_if_clicked(self, pos):
        """Возвращает шарик в ячейке, если клик по координатам pos пришелся на таковой"""

        for row in self.matrix:
            for ball in row:
                if ball:
                    rect = pygame.Rect(ball.pos_x, ball.pos_y, 58, 58)
                    if rect.collidepoint(pos):
                        return ball

        return None

    def get_empty_cell_if_clicked(self, pos):
        """Возвращает кортеж позиции ячейки в матрице, если клик был по ней"""
        for i in range(len(self.matrix)):
            for j in range(len(self.matrix[i])):
                cell_coords = self.matrix_pos_to_grid_coords((i, j))
                rect = pygame.Rect(cell_coords[0], cell_coords[1], 58, 58)
                if rect.collidepoint(pos):
                    return i, j

        return None
