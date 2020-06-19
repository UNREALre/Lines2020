#! /usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
import pygame.freetype
import os
from utils import pygame_textinput
from config import PROJECT_ROOT

pygame.freetype.init()

PRETENDER_NAME = 'Претендент'
WINNER_TEXT = 'Вы победили короля! Введите новое имя Короля!'
LOSER_TEXT = 'К сожалению, Вы проиграли!'
LOSER_TEXT2 = 'Нажмите F5, чтобы начать сначала.'
HELP_TEXT = 'F5 - начать сначала. ESC - выход.'
PRETENDER_COLUMN_HEIGHT = 10
KING_COLUMN_HEIGHT = 370

HEADER_HEIGHT = 100
FOOTER_HEIGHT = 100

UI_COLOR = (186, 186, 186)
SCORE_BG_COLOR = (0, 0, 0)
SCORE_FONT_COLOR = (255, 126, 0)
COLUMN_COLOR = (132, 112, 110)
WINNER_TEXT_COLOR = (226, 127, 0)
HELP_TEXT_COLOR = (226, 127, 0)

SCORE_FONT = pygame.freetype.Font(os.path.join(PROJECT_ROOT, 'fonts/scoreboard.ttf'), 45)
TEXT_FONT = pygame.freetype.Font(os.path.join(PROJECT_ROOT, 'fonts/mr_CoasterG Black.otf'), 35)
KING_SPRITE = os.path.join(PROJECT_ROOT, 'sprites/king.png')
PRETENDER_SPRITE = os.path.join(PROJECT_ROOT, 'sprites/pretender.png')
SAD_SPRITE = os.path.join(PROJECT_ROOT, 'sprites/sad.png')
COLUMN = os.path.join(PROJECT_ROOT, 'sprites/column.svg')

SCORE_CENTER_PADDING = 400  # отступ для окна со счетом от центра
PERSON_CENTER_PADDING = 500  # отступ для короля от центра
PRETENDER_CENTER_PADDING = 330  # отступ для претендента от центра


class UI:
    """Класс для работы с интерфейсом пользователя"""

    def __init__(self, surface):
        self.render_panels(surface)
        scr_width, scr_height = pygame.display.get_surface().get_size()
        self._x_centered = scr_width / 2
        self._y_centered = scr_height / 2

    def render_panels(self, surface):
        """Рисуем подложки для хедера и футера"""

        scr_width, scr_height = surface.get_size()
        pygame.draw.rect(surface, pygame.Color('black'), (0, 0, scr_width, scr_height))

        pygame.draw.rect(surface, UI_COLOR, (0, 0, scr_width, HEADER_HEIGHT))
        pygame.draw.rect(surface, UI_COLOR, (0, scr_height - FOOTER_HEIGHT, scr_width, FOOTER_HEIGHT))

        scr_width, scr_height = pygame.display.get_surface().get_size()
        help_pos = (scr_width/2 - 300, scr_height - 70)
        help_pos_text = (help_pos[0] + 10, help_pos[1] + 10)
        help_dim = (550, 50)
        pygame.draw.rect(surface, pygame.Color('black'), [help_pos, help_dim])
        TEXT_FONT.render_to(surface, help_pos_text, HELP_TEXT, HELP_TEXT_COLOR)

    def render_scores(self, surface, top, current):
        """Выводит счета лидера и текущего пользователя"""

        # Рисуем панели для отображения счетов лидера и текущего счета пользователя
        top_score_len = len(str(top['score']))
        delta_width = (top_score_len - 3) * 25
        pygame.draw.rect(surface, SCORE_BG_COLOR, (self._x_centered - SCORE_CENTER_PADDING, 25, 85 + delta_width, 50))
        SCORE_FONT.render_to(surface,
                             (self._x_centered - SCORE_CENTER_PADDING + 10, 35),
                             str(top['score']),
                             SCORE_FONT_COLOR)

        current_user_len = len(str(current))
        delta_width = (current_user_len - 3) * 25
        pygame.draw.rect(surface, SCORE_BG_COLOR, (self._x_centered + SCORE_CENTER_PADDING, 25, 85 + delta_width, 50))
        SCORE_FONT.render_to(surface,
                             (self._x_centered + SCORE_CENTER_PADDING + 10, 35),
                             str(current),
                             SCORE_FONT_COLOR)

        # Рисуем постаменты с лидером и игроком

        if current > top['score']:
            # У нас новый король
            # Закрашиваем все, что было в колонке слева
            king_sprite = SAD_SPRITE
            pretender_sprite = KING_SPRITE
        else:
            king_sprite = KING_SPRITE
            pretender_sprite = PRETENDER_SPRITE

        king = pygame.image.load(king_sprite)
        surface.blit(king, (self._x_centered - PERSON_CENTER_PADDING, self._y_centered - 250))
        pygame.draw.rect(surface,
                         COLUMN_COLOR,
                         [self._x_centered - PERSON_CENTER_PADDING, self._y_centered - 105, 170, KING_COLUMN_HEIGHT])
        TEXT_FONT.render_to(surface,
                            (self._x_centered - PERSON_CENTER_PADDING, self._y_centered + 280),
                            str(top['name']),
                            SCORE_FONT_COLOR)

        # Закрашиваем все, что было в колонке справа
        pygame.draw.rect(surface,
                         pygame.Color('black'),
                         [self._x_centered + PRETENDER_CENTER_PADDING, self._y_centered - 250, 170, 520]
                         )
        # Вычисляем, насколько надо увеличить постамент претендента в зависимости от счета текущего
        score_delta = (current / top['score']) * 100
        if score_delta >= 100:
            pretender_height = KING_COLUMN_HEIGHT
        elif score_delta > 0:
            pretender_height = (KING_COLUMN_HEIGHT / 100) * score_delta
        else:
            pretender_height = PRETENDER_COLUMN_HEIGHT
        height_delta = pretender_height - PRETENDER_COLUMN_HEIGHT

        pretender = pygame.image.load(pretender_sprite)
        surface.blit(pretender, (self._x_centered + PRETENDER_CENTER_PADDING, self._y_centered + 110 - height_delta))

        pygame.draw.rect(surface,
                         COLUMN_COLOR,
                         [self._x_centered + PRETENDER_CENTER_PADDING, self._y_centered + 250 - height_delta, 170, pretender_height]
                         )
        TEXT_FONT.render_to(surface,
                            (self._x_centered + PRETENDER_CENTER_PADDING, self._y_centered + 280),
                            PRETENDER_NAME,
                            SCORE_FONT_COLOR
                            )

    def init_text_input(self):
        """Инициализация инпута для ввода имени пользователя"""

        return pygame_textinput.TextInput(
            font_family='fonts/mr_CoasterG Black.otf',
            repeat_keys_initial_ms=1000,
            max_string_length=10
        )

    def show_input_name(self, surface, text_input):
        """Показывает интерфейс ввода имени победителя"""

        dialogue_pos = (self._x_centered - 390, self._y_centered - 100)
        dialogue_dim = (800, 100)
        header_pos = (dialogue_pos[0] + 27, dialogue_pos[1] + 10)
        input_pos = (dialogue_pos[0] + 27, dialogue_pos[1] + 50)
        pygame.draw.rect(surface, UI_COLOR, [dialogue_pos, dialogue_dim])
        TEXT_FONT.render_to(surface, header_pos, WINNER_TEXT, WINNER_TEXT_COLOR)
        surface.blit(text_input.get_surface(), input_pos)

    def render_next_colors(self, surface, next_colors):
        """Рендерит область, показывающую, какие шары по цвету будут следующими выброшены в игру"""

        next_pos = (self._x_centered-100, 25)
        for i in range(len(next_colors)):
            delta_x = i * 70
            surface.blit(next_colors[i][0], (next_pos[0] + delta_x, next_pos[1]))

    def game_over(self, surface):
        """Показывает окно завершения игры"""

        dialogue_pos = (self._x_centered - 390, self._y_centered - 100)
        dialogue_dim = (800, 100)
        header_pos = (dialogue_pos[0] + 27, dialogue_pos[1] + 10)
        sub_header_pos = (dialogue_pos[0] + 27, dialogue_pos[1] + 60)
        pygame.draw.rect(surface, UI_COLOR, [dialogue_pos, dialogue_dim])
        TEXT_FONT.render_to(surface, header_pos, LOSER_TEXT, WINNER_TEXT_COLOR)
        TEXT_FONT.render_to(surface, sub_header_pos, LOSER_TEXT2, WINNER_TEXT_COLOR)