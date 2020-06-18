#! /usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
import ctypes
from config import app_config, app_logger
from classes.Game import Game
from classes.Grid import Grid
from classes.Ball import Ball
from classes.UI import UI

pygame.init()

# Заглавие окна
pygame.display.set_caption(app_config['app']['name'].get())

# Две строчки ниже хак, чтобы FULLSCREEN рисовался строго по границам монитора, а не шире, как по умолчанию
ctypes.windll.user32.SetProcessDPIAware()
true_res = (ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1))
window = pygame.display.set_mode(true_res, pygame.FULLSCREEN)

# Инициализируем UI
user_interface = UI(window)

# Инициализируем Grid
grid = Grid()
grid.draw(window)

# Головная игровая логика
game = Game(window, grid, user_interface)
game.start()
