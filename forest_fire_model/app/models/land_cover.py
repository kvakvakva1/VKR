from enum import Enum
import matplotlib.colors as colors

class LandCoverType(Enum):
    """
    Перечисление типов растительности и состояний пожара.
    
    Значения:
        1-17: Типы растительности (например, EVERGREEN_NEEDLELEAF, URBAN).
        18-21: Состояния пожара (IGNITION, FIRE, BURNING_OUT, ASH).
    """
    EVERGREEN_NEEDLELEAF = 1
    EVERGREEN_BROADLEAF = 2
    DECIDUOUS_NEEDLELEAF = 3
    DECIDUOUS_BROADLEAF = 4
    MIXED_FOREST = 5
    CLOSED_SHRUBLANDS = 6
    OPEN_SHRUBLANDS = 7
    WOODY_SAVANNAS = 8
    SAVANNAS = 9
    GRASSLANDS = 10
    PERMANENT_WETLANDS = 11
    CROPLANDS = 12
    URBAN = 13
    CROPLAND_MOSAIC = 14
    SNOW_ICE = 15
    BARREN = 16
    WATER = 17

    # Состояния пожара
    IGNITION = 18
    FIRE = 19
    BURNING_OUT = 20
    ASH = 21

    @classmethod
    def get_color_map(cls):
        """
        Возвращает цветовую карту для визуализации.
        
        Returns:
            colors.ListedColormap: Цветовая карта, где каждому типу/состоянию соответствует цвет.
        """
        colors_list = [
            '#05450a', '#086a10', '#54a708', '#78d203', '#009900',
            '#c6b044', '#dcd159', '#dade48', '#fbff13', '#b6ff05',
            '#27ff87', '#c24f44', '#a5a5a5', '#ff6d4c', '#69fff8',
            '#f9ffa4', '#1c0dff', 'yellow', 'red', 'orange', '#4b4b4b'
        ]
        return colors.ListedColormap(colors_list)

    @classmethod
    def get_bounds(cls):
        """
        Возвращает границы для нормализации цветовой карты.
        
        Returns:
            list: Список границ от 1 до 22.
        """
        return list(range(1, 23))

    @classmethod
    def get_ignition_modifier(cls, land_type: int) -> float:
        """
        Возвращает модификатор вероятности возгорания для типа растительности.
        
        Args:
            land_type (int): Тип растительности.
            
        Returns:
            float: Модификатор (0.0-1.0), где 1.0 - высокая вероятность возгорания.
        """
        modifiers = {
            1: 0.9, 2: 0.7, 3: 0.8, 4: 0.6, 5: 0.75,
            6: 0.5, 7: 0.5, 8: 0.4, 9: 0.3, 10: 0.2,
            11: 0.1, 12: 0.3, 13: 0.05, 14: 0.25, 15: 0.0,
            16: 0.05, 17: 0.0
        }
        return modifiers.get(land_type, 0.0)