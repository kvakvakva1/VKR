import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.animation as animation
from typing import List
from scipy import ndimage

from .cell import ForestFireCell, CellState
from .wind import WindDirection
from .fuzzy_logic import FuzzyFireController

class ForestFireAutomaton:
    """Клеточный автомат для моделирования лесного пожара"""
    
    def __init__(self, width: int, height: int, 
                 wind_direction: WindDirection = WindDirection.N, 
                 wind_speed: float = 0.0,
                 humidity: float = 50.0):
        self.width = width
        self.height = height
        self.grid = [[ForestFireCell() for _ in range(width)] for _ in range(height)]
        self.wind_direction = wind_direction
        self.wind_speed = wind_speed
        self.humidity = humidity
        self.fuzzy_controller = FuzzyFireController()
        self.wind_effect_matrix = self._create_wind_effect_matrix()
        self.height_map = self._generate_height_map(width, height)
    
    def _generate_height_map(self, width: int, height: int) -> np.ndarray:
        # Плавные перепады
        height_map = np.random.rand(height, width)
        height_map = ndimage.gaussian_filter(height_map, sigma=5) * 100
        
        return height_map
    
    def _create_wind_effect_matrix(self) -> List[List[float]]:
        """Создание матрицы влияния ветра"""
        matrix = [[1.0 for _ in range(3)] for _ in range(3)]
        matrix[1][1] = 0.0
        
        if self.wind_speed == 0:
            return matrix
        
        main_reduction = max(0.1, 1 - self.wind_speed/30)
        side_reduction = max(0.3, 1 - self.wind_speed/40)
        
        if self.wind_direction == WindDirection.N:
            matrix[0][1] = main_reduction
            matrix[0][0] = side_reduction
            matrix[0][2] = side_reduction
        elif self.wind_direction == WindDirection.NE:
            matrix[0][2] = main_reduction
            matrix[0][1] = side_reduction
            matrix[1][2] = side_reduction
        elif self.wind_direction == WindDirection.E:
            matrix[1][2] = main_reduction
            matrix[0][2] = side_reduction
            matrix[2][2] = side_reduction
        elif self.wind_direction == WindDirection.SE:
            matrix[2][2] = main_reduction
            matrix[1][2] = side_reduction
            matrix[2][1] = side_reduction
        elif self.wind_direction == WindDirection.S:
            matrix[2][1] = main_reduction
            matrix[2][0] = side_reduction
            matrix[2][2] = side_reduction
        elif self.wind_direction == WindDirection.SW:
            matrix[2][0] = main_reduction
            matrix[2][1] = side_reduction
            matrix[1][0] = side_reduction
        elif self.wind_direction == WindDirection.W:
            matrix[1][0] = main_reduction
            matrix[0][0] = side_reduction
            matrix[2][0] = side_reduction
        elif self.wind_direction == WindDirection.NW:
            matrix[0][0] = main_reduction
            matrix[0][1] = side_reduction
            matrix[1][0] = side_reduction
            
        return matrix
    
    def ignite_random_cells(self, count: int = 1):
        """Зажигание случайных клеток"""
        for _ in range(count):
            x, y = random.randint(0, self.width-1), random.randint(0, self.height-1)
            self.grid[y][x].state = CellState.IGNITION
    
    def update(self):
        """Обновление состояния автомата"""
        for y in range(self.height):
            for x in range(self.width):
                self._update_cell(x, y)
        
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x].update()
    
    def _update_cell(self, x: int, y: int):
        """Обновление состояния клетки"""
        cell = self.grid[y][x]
        
        if cell.state == CellState.FOREST:
            burning_neighbors = self._count_burning_neighbors(x, y)
            if burning_neighbors > 0:
                prob = self.fuzzy_controller.compute_fire_probability(
                    self.wind_speed, self.humidity, burning_neighbors)
                if random.random() * 100 < prob:
                    cell.next_state = CellState.IGNITION
        elif cell.state == CellState.IGNITION and cell.fire_duration >= 1:
            cell.next_state = CellState.FIRE
        elif cell.state == CellState.FIRE and cell.fire_duration >= 3:
            cell.next_state = CellState.BURNING_OUT
        elif cell.state == CellState.BURNING_OUT and cell.fire_duration >= 5:
            cell.next_state = CellState.ASH
    
    def _count_burning_neighbors(self, x: int, y: int) -> int:
        """Подсчет горящих соседей с учетом высоты"""
        count = 0
        current_height = self.height_map[y][x]
        
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.grid[ny][nx].state in [CellState.IGNITION, CellState.FIRE, CellState.BURNING_OUT]:
                        neighbor_height = self.height_map[ny][nx]
                        height_diff = neighbor_height - current_height
                        
                        # Базовый вес от ветра
                        weight = self.wind_effect_matrix[dy+1][dx+1]
                        
                        # Модификатор от высоты (эмпирическая формула)
                        height_factor = 1.0 + 0.05 * height_diff  # +5% за каждый метр подъема
                        weight *= height_factor
                        
                        if random.random() < weight:
                            count += 1
        return count

    def visualize(self):
        """Визуализация состояния автомата"""
        # Числовое представление состояний
        state_to_num = {
            CellState.FOREST: 0,
            CellState.IGNITION: 1,
            CellState.FIRE: 2,
            CellState.BURNING_OUT: 3,
            CellState.ASH: 4
        }
        
        grid_numeric = np.array([[state_to_num[cell.state] for cell in row] for row in self.grid])
        
        # Цветовая карта
        cmap = colors.ListedColormap(['green', 'yellow', 'red', 'orange', 'black'])
        bounds = [0, 1, 2, 3, 4, 5]
        norm = colors.BoundaryNorm(bounds, cmap.N)
        
        plt.figure(figsize=(10, 10))
        img = plt.imshow(grid_numeric, cmap=cmap, norm=norm)
        
        # Создание легенды
        patches = [plt.Rectangle((0,0),1,1, fc=cmap(i)) for i in range(5)]
        labels = ['Лес', 'Возгорание', 'Пожар', 'Затухание', 'Зола']
        plt.legend(patches, labels, bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.title(f"Forest Fire\nWind: {self.wind_direction.name} {self.wind_speed}m/s, Humidity: {self.humidity}%")
        plt.axis('off')
        plt.tight_layout()
        plt.show()

class AnimatedForestFire(ForestFireAutomaton):
    """Расширенный класс для анимации лесного пожара"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.setup_visualization()
    
    def setup_visualization(self):
        """Настройка визуализации с учетом высоты"""
        # Основная визуализация состояний
        state_to_num = {
            CellState.FOREST: 0,
            CellState.IGNITION: 1,
            CellState.FIRE: 2,
            CellState.BURNING_OUT: 3,
            CellState.ASH: 4
        }
        
        self.grid_numeric = np.array([[state_to_num[cell.state] for cell in row] for row in self.grid])
        
        # Создаем композитное изображение (состояния + высоты)
        self.cmap_states = colors.ListedColormap(['green', 'yellow', 'red', 'orange', 'black'])
        self.cmap_heights = plt.cm.terrain  # Цветовая карта для высот
        
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(15, 7))
        
        # Левая панель: состояния
        self.img1 = self.ax1.imshow(self.grid_numeric, cmap=self.cmap_states)
        
        # Правая панель: высоты
        self.img2 = self.ax2.imshow(self.height_map, cmap=self.cmap_heights)
        
        # Настройка легенды и подписей
        patches = [plt.Rectangle((0,0),1,1, fc=self.cmap_states(i)) for i in range(5)]
        labels = ['Лес', 'Возгорание', 'Пожар', 'Затухание', 'Зола']
        self.ax1.legend(patches, labels, bbox_to_anchor=(1.05, 1), loc='upper left')
        
        self.ax1.set_title(f"Состояние пожара\nВетер: {self.wind_direction.name} {self.wind_speed}м/с")
        self.ax2.set_title("Карта высот")
        
        plt.colorbar(self.img2, ax=self.ax2, label='Высота (м)')
        plt.tight_layout()
    
    def update_frame(self, frame):
        """Обновление кадра анимации"""
        self.update()
        
        # Обновление числового представления
        state_to_num = {
            CellState.FOREST: 0,
            CellState.IGNITION: 1,
            CellState.FIRE: 2,
            CellState.BURNING_OUT: 3,
            CellState.ASH: 4
        }
        
        self.grid_numeric = np.array([[state_to_num[cell.state] for cell in row] for row in self.grid])
        self.img.set_array(self.grid_numeric)
        
        # Обновление заголовка с номером кадра
        self.ax.set_title(f"Forest Fire (Step: {frame})\nWind: {self.wind_direction.name} {self.wind_speed}m/s, Humidity: {self.humidity}%")
        
        return [self.img]
    
    def animate(self, frames=50, interval=200):
        """Создание анимации"""
        self.ani = animation.FuncAnimation(
            self.fig, 
            self.update_frame, 
            frames=frames,
            interval=interval,
            blit=True
        )
        plt.close()
        return self.ani