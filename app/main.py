from app.models.animated_forest_fire import AnimatedForestFire
from app.models.wind import WindDirection
from app.models.cell import CellState

width, height = 1000, 1000
wind_dir = WindDirection.NW
wind_speed = 24.0
humidity = 30.0
    
automaton = AnimatedForestFire(width, height, wind_dir, wind_speed, humidity)
automaton.grid[500][500].state = CellState.IGNITION
    
ani = automaton.animate(frames=400, interval=300)
ani.save('1.gif', writer='pillow', fps=5, dpi=100)
