from enum import Enum

#Состояния клетки
class CellState(Enum):
    FOREST = 0       # Негоревший лес
    IGNITION = 1     # Начальная стадия пожара
    FIRE = 2         # Активный пожар
    BURNING_OUT = 3  # Затухание
    ASH = 4          # Зола

#Класс клетки
class ForestFireCell:
    
    def __init__(self, state: CellState = CellState.FOREST):
        self.state = state
        self.next_state = state
        self.fire_duration = 0
        
    #Обновление состояния клетки
    def update(self):
        self.state = self.next_state
        if self.state in [CellState.IGNITION, CellState.FIRE, CellState.BURNING_OUT]:
            self.fire_duration += 1