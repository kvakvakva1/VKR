from enum import Enum
from .land_cover import LandCoverType

class CellState(Enum):
    """
    Перечисление состояний клетки в модели лесного пожара.
    
    Значения:
        FOREST: Негоревший лес (исходное состояние).
        IGNITION: Начальная стадия пожара (только что загорелась).
        FIRE: Активный пожар (полноценное горение).
        BURNING_OUT: Затухание (пожар ослабевает).
        ASH: Зола (окончательное состояние после пожара).
    """
    FOREST = 0
    IGNITION = 1
    FIRE = 2
    BURNING_OUT = 3
    ASH = 4

class ForestFireCell:
    """
    Класс, представляющий клетку в модели лесного пожара.
    
    Атрибуты:
        land_type (int): Тип растительности (соответствует LandCoverType).
        state (CellState): Текущее состояние клетки.
        next_state (CellState): Состояние, которое будет применено при следующем обновлении.
        fire_duration (int): Продолжительность горения (в шагах моделирования).
    """
    def __init__(self, land_type: int = 1, state: CellState = CellState.FOREST):
        """
        Инициализация клетки.
        
        Args:
            land_type (int): Тип растительности (по умолчанию 1 - EVERGREEN_NEEDLELEAF).
            state (CellState): Начальное состояние (по умолчанию FOREST).
        """
        self.land_type = land_type
        self.state = state
        self.next_state = state
        self.fire_duration = 0  # Счетчик времени горения
        
    def update(self):
        """
        Обновляет состояние клетки:
        - Применяет next_state как новое состояние.
        - Увеличивает счетчик fire_duration, если клетка горит.
        """
        self.state = self.next_state
        if self.state in [CellState.IGNITION, CellState.FIRE, CellState.BURNING_OUT]:
            self.fire_duration += 1