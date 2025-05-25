from app.models.animated_forest_fire import AnimatedForestFire
from app.models.wind import WindDirection
from app.models.cell import CellState
import matplotlib.animation as animation

land_cover_file = "data/input/map4.tif"
wind_dir = WindDirection.SE
wind_speed = 12.0
humidity = 45.0
temperature = 18.0
    
automaton = AnimatedForestFire(
    land_cover_file=land_cover_file,
    wind_direction=wind_dir,
    wind_speed=wind_speed,
    humidity=humidity,
    temperature=temperature
)

automaton.grid[automaton.height // 2][automaton.width // 2].state = CellState.IGNITION
automaton.grid[(automaton.height // 2)+1][automaton.width // 2].state = CellState.IGNITION

# Создаем writer с буферизацией в файл
Writer = animation.writers['ffmpeg']
writer = Writer(fps=5, metadata=dict(title='Forest Fire Simulation', artist='Your Name'),
                bitrate=3000, extra_args=['-vcodec', 'libx264', '-pix_fmt', 'yuv420p'])
ani = automaton.animate(frames=800, interval=500)
#ani.save('forest_fire.gif', writer='pillow', fps=5, dpi=100)

ani.save('data/output/forest_fire.mp4', writer=writer)