import random
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.animation as animation
from typing import List
from scipy import ndimage
import rasterio

from .cell import ForestFireCell, CellState
from .wind import WindDirection
from .fuzzy_logic import FuzzyFireController
from .land_cover import LandCoverType

class ForestFireAutomaton:
    def __init__(self, land_cover_file: str,
                 fuzzy_controller: FuzzyFireController, 
                 wind_direction: WindDirection = WindDirection.N, 
                 wind_speed: float = 0.0,
                 humidity: float = 50.0,
                 temperature: float = 15.0):
        """
        Инициализация автомата для моделирования лесного пожара.
        
        Args:
            land_cover_file (str): Путь к файлу с картой растительности (TIFF-формат).
            wind_direction (WindDirection): Направление ветра (по умолчанию - север).
            wind_speed (float): Скорость ветра (по умолчанию 0.0 м/с).
            humidity (float): Влажность воздуха (по умолчанию 50.0%).
        """
        # Загрузка карты растительности из файла
        self.land_cover = self.load_land_cover_tif(land_cover_file)
        self.height, self.width = self.land_cover.shape
        
        # Инициализация сетки клеток на основе карты растительности
        self.grid = [[ForestFireCell(land_type=int(self.land_cover[y][x])) 
                     for x in range(self.width)] for y in range(self.height)]
        
        # Установка параметров окружающей среды
        self.wind_direction = wind_direction
        self.wind_speed = wind_speed
        self.humidity = humidity
        self.temperature = temperature
        
        # Инициализация контроллера нечеткой логики для расчета вероятности возгорания
        self.fuzzy_controller = fuzzy_controller
        
        # Создание матрицы влияния ветра на распространение огня
        self.wind_effect_matrix = self._create_wind_effect_matrix()

    def load_land_cover_tif(self, file_path: str) -> np.ndarray:
        """
        Загружает TIFF-файл карты растительности.
        
        Args:
            file_path (str): Путь к файлу.
            
        Returns:
            np.ndarray: Массив с данными о типе растительности.
        """
        with rasterio.open(file_path) as src:
            data = src.read(1)  # Читаем первый канал
            return data

    def _create_wind_effect_matrix(self) -> List[List[float]]:
        """
        Создает матрицу 3x3, описывающую влияние ветра на распространение огня.
        
        Returns:
            List[List[float]]: Матрица влияния ветра.
        """
        matrix = [[-0.5 for _ in range(3)] for _ in range(3)]
        matrix[1][1] = 0.0  # Центральная клетка (текущая) не учитывается
        
        if self.wind_speed == 0:
            return matrix
        
        # Настройка матрицы в зависимости от направления ветра
        if self.wind_direction == WindDirection.N:
            matrix[0][1] = 1  # Север
            matrix[0][0] = 0.5  # Северо-запад
            matrix[0][2] = 0.5  # Северо-восток
            matrix[2][0] = -1  # Юг
            matrix[2][1] = -1  # Юго-запад
            matrix[2][2] = -1  # Юго-восток
        elif self.wind_direction == WindDirection.NE:
            matrix[0][2] = 1  # Северо-восток
            matrix[0][1] = 1  # Север
            matrix[1][2] = 1  # Восток
            matrix[2][0] = -1  # Юго-запад
            matrix[1][0] = -1  # Запад
            matrix[2][0] = -1  # Юг
        elif self.wind_direction == WindDirection.E:
            matrix[1][2] = 1  # Восток
            matrix[0][2] = 0.5  # Северо-восток
            matrix[2][2] = 0.5  # Юго-восток
            matrix[1][0] = -1  # Запад
            matrix[0][0] = -1  # Северо-запад
            matrix[2][0] = -1  # Юго-запад
        elif self.wind_direction == WindDirection.SE:
            matrix[2][2] = 1  # Юго-восток
            matrix[1][2] = 1  # Восток
            matrix[2][1] = 1  # Юг
            matrix[0][0] = -1  # Северо-запад
            matrix[0][1] = -1  # Север
            matrix[1][0] = -1  # Запад
        elif self.wind_direction == WindDirection.S:
            matrix[2][1] = 1  # Юг
            matrix[2][0] = 0.5  # Юго-запад
            matrix[2][2] = 0.5  # Юго-восток
            matrix[0][1] = -1  # Север
            matrix[0][0] = -1  # Северо-запад
            matrix[0][2] = -1  # Северо-восток
        elif self.wind_direction == WindDirection.SW:
            matrix[2][0] = 1  # Юго-запад
            matrix[2][1] = 1  # Юг
            matrix[1][0] = 1  # Запад
            matrix[0][2] = -1  # Северо-восток
            matrix[0][1] = -1  # Север
            matrix[1][2] = -1  # Восток
        elif self.wind_direction == WindDirection.W:
            matrix[1][0] = 1  # Запад
            matrix[0][0] = 0.5  # Северо-запад
            matrix[2][0] = 0.5  # Юго-запад
            matrix[1][2] = -1  # Восток 
            matrix[0][2] = -1  # Северо-восток
            matrix[2][2] = -1  # Юго-восток
        elif self.wind_direction == WindDirection.NW:
            matrix[0][0] = 1  # Северо-запад
            matrix[0][1] = 1  # Север
            matrix[1][0] = 1  # Запад
            matrix[2][2] = -1  # Юго-восток
            matrix[1][2] = -1  # Восток
            matrix[2][1] = -1  # Юг
            
        return matrix
    
    def ignite_random_cells(self, count: int = 1):
        """
        Зажигает случайные клетки леса.
        
        Args:
            count (int): Количество клеток для поджига (по умолчанию 1).
        """
        for _ in range(count):
            x, y = random.randint(0, self.width-1), random.randint(0, self.height-1)
            if self.grid[y][x].state == CellState.FOREST:  # Зажигаем только лесные клетки
                self.grid[y][x].state = CellState.IGNITION
    
    def update(self):
        """
        Обновляет состояние всех клеток в сетке.
        """
        # Фаза 1: Расчет следующего состояния для всех клеток
        for y in range(self.height):
            for x in range(self.width):
                self._update_cell(x, y)
        
        # Фаза 2: Применение следующего состояния
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x].update()
    
    def _update_cell(self, x: int, y: int):
        """
        Обновляет состояние конкретной клетки.
        
        Args:
            x (int): Координата X клетки.
            y (int): Координата Y клетки.
        """
        cell = self.grid[y][x]
        
        if cell.state == CellState.FOREST:
            # Проверяем горящих соседей
            burning_neighbors, wind_dir = self._count_burning_neighbors(x, y)
            if burning_neighbors > 0:
                # Рассчитываем вероятность возгорания с учетом нечеткой логики
                prob = self.fuzzy_controller.compute_fire_probability(
                    self.wind_speed * wind_dir, self.humidity, burning_neighbors, self.temperature)
                
                # Учитываем тип растительности
                prob *= LandCoverType.get_ignition_modifier(cell.land_type)
                
                # Применяем вероятность возгорания
                if random.random() * 100 < prob:
                    cell.next_state = CellState.IGNITION
        # Переходы между состояниями горения
        elif cell.state == CellState.IGNITION and cell.fire_duration >= 1:
            cell.next_state = CellState.FIRE
        elif cell.state == CellState.FIRE and cell.fire_duration >= 8:
            cell.next_state = CellState.BURNING_OUT
        elif cell.state == CellState.BURNING_OUT and cell.fire_duration >= 9:
            cell.next_state = CellState.ASH
    
    def _count_burning_neighbors(self, x: int, y: int) -> int:
        """
        Подсчитывает количество горящих соседей с учетом ветра и рельефа.
        
        Args:
            x (int): Координата X клетки.
            y (int): Координата Y клетки.
            
        Returns:
            int: Количество горящих соседей с учетом весов.
        """
        count = 0
        wind_dir = 0
        current_height = self.height_map[y][x] if hasattr(self, 'height_map') else 0
        
        # Проверяем все 8 соседних клеток
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue  # Пропускаем текущую клетку
                
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.grid[ny][nx].state in [CellState.IGNITION, CellState.FIRE, CellState.BURNING_OUT]:
                        neighbor_height = self.height_map[ny][nx] if hasattr(self, 'height_map') else 0
                        height_diff = neighbor_height - current_height
                        
                        count += 1

                        weight = self.wind_effect_matrix[dy+1][dx+1]

                        if (weight == 1):
                            wind_dir = 1
                        elif (weight == 0.5 and wind_dir != 1):
                            wind_dir = 0
                        elif (weight == -1 and wind_dir != 1):
                            wind_dir = -0.6
                        elif (weight == -0.5 and wind_dir != 1):
                            wind_dir = -0.6

        return (count, wind_dir)
    
    def visualize(self):
        """
        Визуализирует текущее состояние сетки с помощью matplotlib.
        """
        # Создаем числовое представление сетки
        grid_numeric = np.zeros((self.height, self.width))
        
        # Заполняем сетку значениями в соответствии с состоянием клеток
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                if cell.state == CellState.FOREST:
                    grid_numeric[y][x] = cell.land_type
                elif cell.state == CellState.IGNITION:
                    grid_numeric[y][x] = LandCoverType.IGNITION.value
                elif cell.state == CellState.FIRE:
                    grid_numeric[y][x] = LandCoverType.FIRE.value
                elif cell.state == CellState.BURNING_OUT:
                    grid_numeric[y][x] = LandCoverType.BURNING_OUT.value
                elif cell.state == CellState.ASH:
                    grid_numeric[y][x] = LandCoverType.ASH.value
        
        # Настраиваем цветовую карту
        cmap = LandCoverType.get_color_map()
        bounds = LandCoverType.get_bounds()
        norm = colors.BoundaryNorm(bounds, len(cmap.colors))
        
        # Создаем изображение
        plt.figure(figsize=(10, 10))
        img = plt.imshow(grid_numeric, cmap=cmap, norm=norm)
        
        # Добавляем заголовок с параметрами моделирования
        plt.title(f"Wind: {self.wind_direction.name} {self.wind_speed}m/s, Humidity: {self.humidity}%, Temp: {self.temperature}°C")
        plt.axis('off')
        plt.tight_layout()
        plt.show()