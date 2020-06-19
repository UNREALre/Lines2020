#! /usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
import random
import collections
import os
import ruamel.yaml
from utils import pygame_textinput
from classes.Grid import Grid
from classes.UI import UI
from classes.Ball import Ball, randomize_sprite
from config import PROJECT_ROOT, app_config, reload_config

app_config = app_config

pygame.mixer.init()
sounds = {
    'error': pygame.mixer.Sound(os.path.join(PROJECT_ROOT, 'audio/error.wav')),
    'victory': pygame.mixer.Sound(os.path.join(PROJECT_ROOT, 'audio/victory.wav'))
}

GAME_STATES = {
    0: "default",
    1: "awaiting_winner_name",
    2: "game_over"
}

CONFIG_FILE = os.path.join(PROJECT_ROOT, 'config.yaml')


class Game:
    """Класс реализующий логику игры"""

    def __init__(self, window, grid, ui, init_balls=5, per_round_balls=3, same_number=5, points_per_ball=5):
        """
        Инициализиурует игру

        :param window: Surface
        :param grid: Grid
        :param ui: UI
        """

        self.window = window
        self.grid = grid
        self.ui = ui
        self.init_balls = init_balls  # кол-во изначально генерируемых на сетке шаров
        self.per_round_balls = per_round_balls  # кол-во добавляемых шаров каждый ход пользователя
        self.same_number = same_number  # кол-во одинаковых по цвету шаров в ряду для их "уничтожения"
        self.points_per_ball = points_per_ball  # кол-во очков за шарик в уничтоженном ряду одинакового цвета
        self.score = 0  # текущий счет пользователя

        self._next_colors = self.predict_next_colors()  # список цветов шаров на следующем шаге
        self._text_input = self.ui.init_text_input()  # тут победитель будет вводить свое имя
        self._game_state = GAME_STATES[0]
        self._run = False

    def start(self):
        """Запускает игру - выбрасывает на сетку 5 случайных шаров"""

        self.rerender_score()

        self.generate_balls(self.init_balls)

        clock = pygame.time.Clock()
        self._run = True
        dt = 0
        while self._run:
            events = pygame.event.get()

            self.fire_event_handling(events)

            self._text_input.update(events)

            self.redraw(dt)

            pygame.display.update()

            clock.tick(30)  # 30 fps
            dt = (dt+1) if dt <= 1000 else 0

        pygame.quit()

    def fire_event_handling(self, events):
        """Обработчка игровых событий"""

        if self._game_state == 'default':
            for event in events:
                if event.type == pygame.QUIT:
                    self._run = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self._run = False
                    elif event.key == pygame.K_F5:
                        # Начать сначала
                        self.end_game()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Определяем был ли клик по шарику

                    pos = pygame.mouse.get_pos()
                    ball = self.grid.get_ball_from_cell_if_clicked(pos)
                    if ball:
                        # Переводим все шарики на доске в состояние "снято выделение"
                        for row in self.grid.matrix:
                            [ball.unselect() for ball in row if ball]

                        ball.select()
                    else:
                        # Проверяем, был ли клик по сетке
                        cell = self.grid.get_empty_cell_if_clicked(pos)
                        if cell:
                            # Клик был по пустой ячейке сетки, надо попытаться туда переместить активный шарик
                            selected_ball = self.get_selected_ball()
                            if selected_ball:
                                if self.move_ball_to_new_cell(selected_ball, cell):
                                    is_destroyed = self.destroy_similar()
                                    if not is_destroyed:
                                        self.generate_balls(self.per_round_balls)

        elif self._game_state == 'awaiting_winner_name':
            for event in events:
                if event.type == pygame.QUIT:
                    self._run = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self._run = False
                    elif event.key == pygame.K_RETURN:
                        self.change_leader(self._text_input.get_text())
                        self.reset()

        elif self._game_state == 'game_over':
            for event in events:
                if event.type == pygame.QUIT:
                    self._run = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self._run = False
                    elif event.key == pygame.K_F5:
                        # Начать сначала
                        self.reset()

    def redraw(self, dt):
        """Перерисовка экрана в зависимости от состояния игры"""

        if self._game_state == 'default':
            # Перерисовываем грид
            self.grid.draw(self.window)

            # Перерисовываем все шарики
            for row in self.grid.matrix:
                for ball in row:
                    if ball:
                        if ball.selected and dt % 5 == 0:
                            ball.animate()
                        ball.draw(self.window)

        elif self._game_state == 'awaiting_winner_name':
            self.enter_name()

    def reset(self):
        """Перезагрузка игры"""

        global app_config
        app_config = reload_config()

        self._next_colors = []
        self.score = 0
        self._game_state = GAME_STATES[0]

        self.ui.render_panels(self.window)
        self.rerender_score()
        self.grid.reset(self.window)
        self.generate_balls(self.init_balls)

    def predict_next_colors(self):
        """Определяет, какого цвета будут шары на следующем вбросе(ходе)"""
        self._next_colors = []
        for i in range(self.per_round_balls):
            self._next_colors.append(randomize_sprite())

    def generate_balls(self, number):
        """Генерирует объекты Ball в количестве равном number шт в случайных ячейках сетки"""

        try:
            for i in range(number):
                matrix_pos = self.get_random_ball_matrix_position()
                pos_x, pos_y = self.grid.matrix_pos_to_grid_coords(matrix_pos)
                predefined_color = self._next_colors[i] if self._next_colors else None
                ball = Ball(pos_x, pos_y, matrix_pos[0], matrix_pos[1], predefined_color)
                self.grid.update_grid(matrix_pos, ball, self.window)

            if self.is_no_empty_cells():
                raise ValueError("Grid is full!")

            self.predict_next_colors()
            self.ui.render_next_colors(self.window, self._next_colors)
            self.destroy_similar()

        except ValueError:
            # Сетка заполнена
            self.end_game()

    def is_no_empty_cells(self):
        """Проверят, что есть свободные места в сетке"""

        if not any(None in cell for cell in self.grid.matrix):
            return True

        return False

    def get_random_ball_matrix_position(self):
        """Возвращает кортеж x,y координаты шара в матрице, если в сетке есть еще место для нового шара"""

        if self.is_no_empty_cells():
            raise ValueError("Grid is full!")

        coords = None
        while not coords:
            row = random.randrange(0, len(self.grid.matrix))
            col = random.randrange(0, len(self.grid.matrix))
            if not self.grid.matrix[row][col]:
                coords = (row, col)

        return coords

    def get_selected_ball(self):
        """Возвращает выбранный шарик, если есть таковой, либо None"""

        for row in self.grid.matrix:
            for ball in row:
                if ball and ball.selected:
                    return ball
        return None

    def move_ball_to_new_cell(self, ball, mx_cell):
        """Пытается переместить шарик в новую ячейку. Получает шарик и кортеж позиции ячейки в сетке"""

        path = self.path_exists((ball.mx_pos_row, ball.mx_pos_col), mx_cell)
        if path:
            # TODO: Анимировать путь движения шарика
            cell_x, cell_y = self.grid.matrix_pos_to_grid_coords(mx_cell)

            self.grid.move_ball_in_matrix(ball, mx_cell)
            ball.update_position((cell_x, cell_y), mx_cell)

            ball.pos_x = cell_x
            ball.pos_y = cell_y
            ball.draw(self.window)
            ball.unselect()

            return True
        else:
            sounds['error'].play()
            return False

    def path_exists(self, from_position, to_position):
        """Определяет, существует ли путь для шарика из позиции from в позицию to"""

        path = self.bfs(from_position, to_position)
        # print(path)
        return path

    def bfs(self, start, goal):
        """Breadth-first search"""

        width = len(self.grid.matrix[0])
        height = len(self.grid.matrix)

        queue = collections.deque([[start]])
        seen = set([start])
        # print(goal)
        while queue:
            path = queue.popleft()
            # print(path)
            # print("====")
            y, x = path[-1]
            # print("x = {}, y = {}".format(x, y))
            if (y, x) == goal:
                return path
            for x2, y2 in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                # print("x2 = {}, y2 = {}".format(x2, y2))
                if 0 <= x2 < width and 0 <= y2 < height and \
                        not isinstance(self.grid.matrix[y2][x2], Ball) and \
                        (x2, y2) not in seen:
                    # print("GOOD x2 = {}, y2 = {}".format(x2, y2))
                    queue.append(path + [(y2, x2)])
                    seen.add((x2, y2))

    def destroy_similar(self):
        """Ищет в матрице одинаковые по цвету и уничтожает, если есть ряд из N одинаковых по цвету"""

        for i in range(len(self.grid.matrix)):
            for j in range(len(self.grid.matrix[i])):
                if self.grid.matrix[i][j]:
                    current_ball = self.grid.matrix[i][j]
                    same_color_positions = self.get_same_colored_neighbors((i, j), current_ball.color)

                    if len(same_color_positions) >= self.same_number:
                        for matrix_pos in same_color_positions:
                            self.grid.delete_from_matrix(matrix_pos)

                        # 10 очков за 5 шариков, а за доп - начисляем еще
                        self.score += 10 + (len(same_color_positions)-5)*self.points_per_ball
                        self.rerender_score()

                        return True
        return False

    def get_same_colored_neighbors(self, current_mx_pos, color):
        """Возвращает список кортежей позиций шаров матрицы, соседних с текущим шаром и такого же цвета"""

        i, j = current_mx_pos
        same_color_positions = [(i, j)]

        # Бежим от текущего элемента направо в поисках одинаковых соседей
        for k in range(j + 1, len(self.grid.matrix[i])):
            if self.grid.matrix[i][k] and color == self.grid.matrix[i][k].color:
                same_color_positions.append((i, k))
            else:
                # Как только что-то не так, то дальше нет смысла продолжать, цепочка соседей нарушена
                break

        if len(same_color_positions) < self.same_number:
            same_color_positions = [(i, j)]
            # Бежим вниз от текущего в поисках одинаковых соседей
            for row_iterator in range(i + 1, len(self.grid.matrix)):
                if self.grid.matrix[row_iterator][j] and color == self.grid.matrix[row_iterator][j].color:
                    same_color_positions.append((row_iterator, j))
                else:
                    break

            if len(same_color_positions) < self.same_number:
                # Проверяем диагонали
                # Сначала проверяем диагональ от текущего шара и налево
                same_color_positions = [(i, j)]
                col_iterator = j
                for row_iterator in range(i + 1, len(self.grid.matrix)):
                    col_iterator -= 1
                    if col_iterator >= 0 and self.grid.matrix[row_iterator][col_iterator] and \
                            color == self.grid.matrix[row_iterator][col_iterator].color:
                        same_color_positions.append((row_iterator, col_iterator))
                    else:
                        break

                if len(same_color_positions) < self.same_number:
                    # Проверяем диагональ от текущего шара и направо
                    same_color_positions = [(i, j)]
                    col_iterator = j
                    for row_iterator in range(i + 1, len(self.grid.matrix)):
                        col_iterator += 1
                        if col_iterator < len(self.grid.matrix[row_iterator]) and \
                                self.grid.matrix[row_iterator][col_iterator] and \
                                color == self.grid.matrix[row_iterator][col_iterator].color:
                            same_color_positions.append((row_iterator, col_iterator))
                        else:
                            break

        return same_color_positions

    def rerender_score(self):
        """Вызывает процесс перерисовки UI со счетами"""

        self.ui.render_scores(self.window,
                              {
                                  'score': app_config['leader']['score'].get(),
                                  'name': app_config['leader']['name'].get()
                              },
                              self.score)

    def enter_name(self):
        """Запускает функционал ввода имени победителя, фиксируем результат игры"""

        self.ui.show_input_name(self.window, self._text_input)

    def change_leader(self, name):
        """Меняет информацию о лидере в конфиге"""

        yaml = ruamel.yaml.YAML()

        yaml.preserve_quotes = True
        with open(CONFIG_FILE) as fp:
            data = yaml.load(fp)
        data['leader']['name'] = name
        data['leader']['score'] = self.score

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            yaml.dump(data, f)

    def end_game(self):
        """Заканчиваем текущую игру"""

        if app_config['leader']['score'].get() < self.score:
            # У нас новый король, показываем интерфейс ввода имени нового короля
            self._game_state = GAME_STATES[1]
        else:
            self.ui.game_over(self.window)
            self._game_state = GAME_STATES[2]
