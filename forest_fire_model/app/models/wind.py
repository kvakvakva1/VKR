from enum import Enum

class WindDirection(Enum):
    """
    Перечисление направлений ветра.
    
    Значения:
        N: Север.
        NE: Северо-восток.
        E: Восток.
        SE: Юго-восток.
        S: Юг.
        SW: Юго-запад.
        W: Запад.
        NW: Северо-запад.
    """
    N = 0
    NE = 1
    E = 2
    SE = 3
    S = 4
    SW = 5
    W = 6
    NW = 7