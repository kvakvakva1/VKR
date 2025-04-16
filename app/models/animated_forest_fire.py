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
from .forest_fire_automaton import ForestFireAutomaton

class AnimatedForestFire(ForestFireAutomaton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.setup_visualization()
        self.animation = None
    
    def setup_visualization(self):
        state_to_num = {
            CellState.FOREST: 0,
            CellState.IGNITION: 1,
            CellState.FIRE: 2,
            CellState.BURNING_OUT: 3,
            CellState.ASH: 4
        }
        
        self.grid_numeric = np.array([[state_to_num[cell.state] for cell in row] for row in self.grid])
        
        # Создание цветовой карты
        self.cmap = colors.ListedColormap(['green', 'yellow', 'red', 'orange', 'black'])
        bounds = [0, 1, 2, 3, 4, 5]
        self.norm = colors.BoundaryNorm(bounds, self.cmap.N)
        
        self.img = self.ax.imshow(self.grid_numeric, cmap=self.cmap, norm=self.norm)
        
        # Создание легенды
        patches = [plt.Rectangle((0,0),1,1, fc=self.cmap(i)) for i in range(5)]
        labels = ['Лес', 'Возгорание', 'Пожар', 'Затухание', 'Зола']
        self.ax.legend(patches, labels, bbox_to_anchor=(1.05, 1), loc='upper left')
        
        self.ax.set_title(f"Направление/скорость ветра: {self.wind_direction.name} {self.wind_speed}м/с, влажность: {self.humidity}%")
        self.ax.axis('off')
        plt.tight_layout()
    
    def update_frame(self, frame):
        self.update()
        
        state_to_num = {
            CellState.FOREST: 0,
            CellState.IGNITION: 1,
            CellState.FIRE: 2,
            CellState.BURNING_OUT: 3,
            CellState.ASH: 4
        }
        
        self.grid_numeric = np.array([[state_to_num[cell.state] for cell in row] for row in self.grid])
        self.img.set_array(self.grid_numeric)
        
        # Обновление заголовка вместе с кадром
        self.ax.set_title(f"Направление/скорость ветра: {self.wind_direction.name} {self.wind_speed}м/с, влажность: {self.humidity}%")
        
        return [self.img]
    
    def animate(self, frames=50, interval=200):
        if hasattr(self, 'animation') and self.animation is not None:
            self.animation.event_source.stop()
        
        self.animation = animation.FuncAnimation(
            self.fig, 
            self.update_frame, 
            frames=frames,
            interval=interval,
            blit=True
        )
        return self.animation