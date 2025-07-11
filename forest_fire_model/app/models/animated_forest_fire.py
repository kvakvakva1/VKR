import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.animation as animation
from .forest_fire_automaton import ForestFireAutomaton
from .land_cover import LandCoverType
from .cell import CellState
from app.models.wind import WindDirection
from .fuzzy_logic import FuzzyFireController

class AnimatedForestFire(ForestFireAutomaton):
    def __init__(self, land_cover_file: str,
                 fuzzy_controller: FuzzyFireController, 
                 wind_direction: WindDirection = WindDirection.N, 
                 wind_speed: float = 0.0,
                 humidity: float = 50.0,
                 temperature: float = 15.0,
                 output_dir: str = 'frames'):
        """
        Инициализация анимированной модели лесного пожара.
        
        Args:
            land_cover_file (str): Путь к файлу с картой растительности (TIFF-формат).
            wind_direction (WindDirection): Направление ветра (по умолчанию - север).
            wind_speed (float): Скорость ветра (по умолчанию 0.0 м/с).
            humidity (float): Влажность воздуха (по умолчанию 50.0%).
        """
        # Инициализация родительского класса ForestFireAutomaton
        super().__init__(land_cover_file, fuzzy_controller, wind_direction, wind_speed, humidity, temperature)
        self.current_frame = 0
        self.max_frames = 0 
        
        # Создание фигуры и оси для анимации
        self.fig, self.ax = plt.subplots(figsize=(38.4, 21.6))
        
        # Настройка визуализации
        self.setup_visualization()
        self.output_dir = 'out'
        os.makedirs(self.output_dir, exist_ok=True)
        # Инициализация переменных для анимации
        self.animation = None
    
    def setup_visualization(self):
        """
        Настраивает визуализацию: цветовую карту, изображение и легенду.
        """
        # Получение цветовой карты и границ для нормализации
        self.cmap = LandCoverType.get_color_map()
        self.bounds = LandCoverType.get_bounds()
        self.norm = colors.BoundaryNorm(self.bounds, len(self.cmap.colors))
        
        # Инициализация числового представления сетки
        self.grid_numeric = np.zeros((self.height, self.width))
        self._update_grid_numeric()  # Заполнение сетки начальными значениями
        
        # Создание изображения на оси
        self.img = self.ax.imshow(self.grid_numeric, cmap=self.cmap, norm=self.norm)
        
        # Настройка заголовка и внешнего вида
        # self.ax.set_title(f"Wind: {self.wind_direction.name} {self.wind_speed}m/s, Humidity: {self.humidity}%, Temp: {self.temperature}°C")
        self.ax.axis('off')
        plt.tight_layout()

    def _update_grid_numeric(self):
        """
        Обновляет числовое представление сетки на основе текущего состояния клеток.
        """
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                if cell.state == CellState.FOREST:
                    self.grid_numeric[y][x] = cell.land_type
                elif cell.state == CellState.IGNITION:
                    self.grid_numeric[y][x] = LandCoverType.IGNITION.value
                elif cell.state == CellState.FIRE:
                    self.grid_numeric[y][x] = LandCoverType.FIRE.value
                elif cell.state == CellState.BURNING_OUT:
                    self.grid_numeric[y][x] = LandCoverType.BURNING_OUT.value
                elif cell.state == CellState.ASH:
                    self.grid_numeric[y][x] = LandCoverType.ASH.value

    def update_frame(self, frame):
        """
        Обновляет кадр анимации: обновляет состояние модели и визуализацию.
        
        Args:
            frame: Номер текущего кадра (не используется, но требуется FuncAnimation).
            
        Returns:
            list: Список обновленных объектов для анимации.
        """
        if self.current_frame > self.max_frames:
            self.animation.event_source.stop()
            return [self.img]

        self.current_frame += 1

        if (self.current_frame % 10 == 0):
            print(f"Текущий кадр: {self.current_frame}")
        
        # Обновление состояния модели
        self.update()
        
        # Обновление числового представления сетки
        self._update_grid_numeric()
        
        # Обновление изображения
        self.img.set_array(self.grid_numeric)
        
        # Обновление заголовка
        # self.ax.set_title(f"Wind: {self.wind_direction.name} {self.wind_speed}m/s, Humidity: {self.humidity}%, Temp: {self.temperature}°C")
        frame_filename = os.path.join(self.output_dir, f"frame_{frame:04d}.png")
        self.fig.savefig(frame_filename, bbox_inches='tight', pad_inches=0, transparent=True)
        
        return [self.img]
    
    def animate(self, frames=50, interval=200):
        """
        Создает и запускает анимацию.
        
        Args:
            frames (int): Количество кадров анимации (по умолчанию 50).
            interval (int): Интервал между кадрами в миллисекундах (по умолчанию 200).
            
        Returns:
            animation.FuncAnimation: Объект анимации.
        """
        self.current_frame = 0
        self.max_frames = frames
        # Остановка предыдущей анимации, если она существует
        if hasattr(self, 'animation') and self.animation is not None:
            self.animation.event_source.stop()
        
        # Создание новой анимации
        self.animation = animation.FuncAnimation(
            self.fig, 
            self.update_frame, 
            frames=frames,
            interval=interval,
            blit=True,  # Оптимизация для анимации
            repeat=False
        )
        
        return self.animation