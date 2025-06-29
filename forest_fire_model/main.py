from app.models.animated_forest_fire import AnimatedForestFire
from app.models.wind import WindDirection
from app.models.cell import CellState
import matplotlib.animation as animation
from app.models.fuzzy_logic import FuzzyFireController
import os

def parse_wind_direction(direction_str):
    try:
        return WindDirection[direction_str.upper()]
    except KeyError:
        print(f"Неверное направление ветра: {direction_str}. Используются значения: {[d.name for d in WindDirection]}")
        return None

def run_simulation():
    print("Инициализация нечеткого контроллера")
    fuzzy = FuzzyFireController()
    print("Инициализация нечеткого контроллера завершена")
    
    input_dir = "data/input"
    output_dir = "data/output"

    while True:
        print("\nВведите параметры сценария моделирования (или 'exit' для выхода):")
        
        land_cover_filename = input("Имя входного файла: ").strip()
        if land_cover_filename.lower() == 'exit':
            break
        land_cover_file = os.path.join(input_dir, land_cover_filename)

        output_filename = input("Имя выходного видеофайла: ").strip()
        output_file = os.path.join(output_dir, output_filename)

        try:
            frames = int(input("Количество кадров: "))
            temperature = float(input("Температура: "))
            humidity = float(input("Влажность: "))
            wind_speed = float(input("Скорость ветра: "))
            wind_direction_str = input("Направление ветра: ").strip()
            wind_direction = parse_wind_direction(wind_direction_str)
            if wind_direction is None:
                continue

            ignition_x = int(input("X координата начального возгорания: "))
            ignition_y = int(input("Y координата начального возгорания: "))
        except ValueError:
            print("Ошибка ввода. Пожалуйста, убедитесь, что числа введены корректно.")
            continue

        # Инициализация модели
        automaton = AnimatedForestFire(
            land_cover_file=land_cover_file,
            fuzzy_controller=fuzzy,
            wind_direction=wind_direction,
            wind_speed=wind_speed,
            humidity=humidity,
            temperature=temperature
        )

        # Установка точки возгорания
        try:
            automaton.grid[ignition_y][ignition_x].state = CellState.IGNITION
            automaton.grid[ignition_y][ignition_x].fire_duration =  -3
        except IndexError:
            print("Неверные координаты возгорания. Попробуйте снова.")
            continue

        # Настройка записи видео
        Writer = animation.writers['ffmpeg']
        writer = Writer(
            fps=5,
            metadata=dict(title='Forest Fire Simulation', artist='Sim Engine'),
            bitrate=3000,
            extra_args=['-vcodec', 'libx264', '-pix_fmt', 'yuv420p']
        )

        print(f"Моделирование... Сохраняется в {output_file}")
        ani = automaton.animate(frames=frames, interval=500)
        ani.save(output_file, writer=writer)
        automaton.animation.event_source.stop()
        print("Сценарий завершён и сохранён.\n")

if __name__ == "__main__":
    run_simulation()