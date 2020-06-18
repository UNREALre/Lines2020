#! /usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
import random
import os
from config import PROJECT_ROOT

default_ball_sprites = [(pygame.image.load(os.path.join(PROJECT_ROOT, 'sprites/sphere-01.png')), '01'),
                        (pygame.image.load(os.path.join(PROJECT_ROOT, 'sprites/sphere-02.png')), '02'),
                        (pygame.image.load(os.path.join(PROJECT_ROOT, 'sprites/sphere-03.png')), '03'),
                        (pygame.image.load(os.path.join(PROJECT_ROOT, 'sprites/sphere-04.png')), '04')
                        # (pygame.image.load(os.path.join(PROJECT_ROOT, 'sprites/sphere-05.png')), '05')
                        ]
anim_delta = 2


class Ball:
    """Класс для работы с шариками"""

    def __init__(self, pos_x, pos_y, mx_pos_row, mx_pos_col):
        """Инициализирует шар"""

        self.sprite, self.color = self.randomize_sprite()
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.mx_pos_row = mx_pos_row  # позиция в матрице сетки по горизонтали
        self.mx_pos_col = mx_pos_col  # позиция в матрице сетки по вертикали
        self.selected = False
        self.anim_state = 'center'  # top, center, down - показывает состояние шарика в моменте

    def randomize_sprite(self):
        """Возвращает случайный спрайт"""

        return default_ball_sprites[random.randrange(0, len(default_ball_sprites))]

    def draw(self, surface):
        """Рисует шарик в окне"""

        surface.blit(self.sprite, (self.pos_x, self.pos_y))

    def select(self):
        """Делает текущий шарик выбранным пользователем, значит анимированным"""

        self.selected = True

    def unselect(self):
        """Снимает флаг выбранности"""

        self.selected = False
        self.anim_state = 'center'

    def animate(self):
        """Анимация шарика"""

        if self.anim_state == 'center':
            # Переводим шарик в статус анимации "наверху", поднимаем его
            self.anim_state = 'top'
            self.pos_y -= anim_delta
        elif self.anim_state == 'top':
            # Шарик был наверху, опустим его
            self.anim_state = 'bottom'
            self.pos_y += anim_delta * 2
        else:
            # Шарик был внизу, поднимем его
            self.anim_state = 'top'
            self.pos_y -= anim_delta * 2

    def update_position(self, grid_pos, mx_pos):
        """Обновляет позицию шарика в сетке (координаты) и в матрице"""

        self.pos_x, self.pos_y = grid_pos
        self.mx_pos_row, self.mx_pos_col = mx_pos
