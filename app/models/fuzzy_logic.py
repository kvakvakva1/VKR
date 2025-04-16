import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class FuzzyFireController:
    
    def __init__(self):
        # Входные переменные
        self.wind_speed = ctrl.Antecedent(np.arange(0, 31, 1), 'wind_speed')
        self.humidity = ctrl.Antecedent(np.arange(0, 101, 1), 'humidity')
        self.burning_neighbors = ctrl.Antecedent(np.arange(0, 9, 1), 'burning_neighbors')
        
        # Выходная переменная
        self.fire_prob = ctrl.Consequent(np.arange(0, 101, 1), 'fire_prob')
        
        # Настройка функций принадлежности
        self._setup_membership_functions()
        # Создание системы правил
        self._setup_rules()
        
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulator = ctrl.ControlSystemSimulation(self.control_system)
    
    #Настройка функций принадлежности
    def _setup_membership_functions(self):
        # Скорость ветра
        self.wind_speed['calm'] = fuzz.trimf(self.wind_speed.universe, [0, 0, 5])
        self.wind_speed['moderate'] = fuzz.trimf(self.wind_speed.universe, [0, 10, 20])
        self.wind_speed['strong'] = fuzz.trimf(self.wind_speed.universe, [10, 20, 30])
        self.wind_speed['storm'] = fuzz.trimf(self.wind_speed.universe, [20, 30, 30])
        
        # Влажность
        self.humidity['dry'] = fuzz.trimf(self.humidity.universe, [0, 0, 30])
        self.humidity['normal'] = fuzz.trimf(self.humidity.universe, [10, 40, 70])
        self.humidity['humid'] = fuzz.trimf(self.humidity.universe, [50, 80, 100])
        self.humidity['very_humid'] = fuzz.trimf(self.humidity.universe, [70, 100, 100])
        
        # Горящие соседи
        self.burning_neighbors['none'] = fuzz.trimf(self.burning_neighbors.universe, [0, 0, 1])
        self.burning_neighbors['few'] = fuzz.trimf(self.burning_neighbors.universe, [0, 2, 4])
        self.burning_neighbors['several'] = fuzz.trimf(self.burning_neighbors.universe, [2, 4, 6])
        self.burning_neighbors['many'] = fuzz.trimf(self.burning_neighbors.universe, [4, 6, 8])
        self.burning_neighbors['all'] = fuzz.trimf(self.burning_neighbors.universe, [6, 8, 8])
        
        # Вероятность возгорания
        self.fire_prob['very_low'] = fuzz.trimf(self.fire_prob.universe, [0, 0, 20])
        self.fire_prob['low'] = fuzz.trimf(self.fire_prob.universe, [0, 20, 40])
        self.fire_prob['medium'] = fuzz.trimf(self.fire_prob.universe, [20, 50, 80])
        self.fire_prob['high'] = fuzz.trimf(self.fire_prob.universe, [60, 80, 100])
        self.fire_prob['very_high'] = fuzz.trimf(self.fire_prob.universe, [80, 100, 100])
    
    #Создание нечеткий правил
    def _setup_rules(self):
        self.rules = []
        
        # Правила для штиля (0-5 м/с)
        self.rules.extend([
            # Очень высокая влажность
            ctrl.Rule(self.wind_speed['calm'] & self.humidity['very_humid'] & self.burning_neighbors['none'], 
                     self.fire_prob['very_low']),
            ctrl.Rule(self.wind_speed['calm'] & self.humidity['very_humid'] & self.burning_neighbors['few'], 
                     self.fire_prob['very_low']),
            ctrl.Rule(self.wind_speed['calm'] & self.humidity['very_humid'] & self.burning_neighbors['several'], 
                     self.fire_prob['low']),
            ctrl.Rule(self.wind_speed['calm'] & self.humidity['very_humid'] & self.burning_neighbors['many'], 
                     self.fire_prob['low']),
            ctrl.Rule(self.wind_speed['calm'] & self.humidity['very_humid'] & self.burning_neighbors['all'], 
                     self.fire_prob['medium']),
            
            # Высокая влажность
            ctrl.Rule(self.wind_speed['calm'] & self.humidity['humid'] & self.burning_neighbors['none'], 
                     self.fire_prob['very_low']),
            ctrl.Rule(self.wind_speed['calm'] & self.humidity['humid'] & self.burning_neighbors['few'], 
                     self.fire_prob['low']),
            ctrl.Rule(self.wind_speed['calm'] & self.humidity['humid'] & self.burning_neighbors['several'], 
                     self.fire_prob['medium']),
            ctrl.Rule(self.wind_speed['calm'] & self.humidity['humid'] & self.burning_neighbors['many'], 
                     self.fire_prob['medium']),
            ctrl.Rule(self.wind_speed['calm'] & self.humidity['humid'] & self.burning_neighbors['all'], 
                     self.fire_prob['high']),
            
            # Нормальная влажность
            ctrl.Rule(self.wind_speed['calm'] & self.humidity['normal'] & self.burning_neighbors['none'], 
                     self.fire_prob['low']),
            ctrl.Rule(self.wind_speed['calm'] & self.humidity['normal'] & self.burning_neighbors['few'], 
                     self.fire_prob['medium']),
            ctrl.Rule(self.wind_speed['calm'] & self.humidity['normal'] & self.burning_neighbors['several'], 
                     self.fire_prob['high']),
            ctrl.Rule(self.wind_speed['calm'] & self.humidity['normal'] & self.burning_neighbors['many'], 
                     self.fire_prob['high']),
            ctrl.Rule(self.wind_speed['calm'] & self.humidity['normal'] & self.burning_neighbors['all'], 
                     self.fire_prob['very_high']),
            
            # Низкая влажность
            ctrl.Rule(self.wind_speed['calm'] & self.humidity['dry'] & self.burning_neighbors['none'], 
                     self.fire_prob['medium']),
            ctrl.Rule(self.wind_speed['calm'] & self.humidity['dry'] & self.burning_neighbors['few'], 
                     self.fire_prob['high']),
            ctrl.Rule(self.wind_speed['calm'] & self.humidity['dry'] & self.burning_neighbors['several'], 
                     self.fire_prob['very_high']),
            ctrl.Rule(self.wind_speed['calm'] & self.humidity['dry'] & self.burning_neighbors['many'], 
                     self.fire_prob['very_high']),
            ctrl.Rule(self.wind_speed['calm'] & self.humidity['dry'] & self.burning_neighbors['all'], 
                     self.fire_prob['very_high']),
        ])
        
        # Правила для умеренного ветра (5-15 м/с)
        self.rules.extend([
            # Очень высокая влажность
            ctrl.Rule(self.wind_speed['moderate'] & self.humidity['very_humid'] & self.burning_neighbors['none'], 
                     self.fire_prob['very_low']),
            ctrl.Rule(self.wind_speed['moderate'] & self.humidity['very_humid'] & self.burning_neighbors['few'], 
                     self.fire_prob['low']),
            ctrl.Rule(self.wind_speed['moderate'] & self.humidity['very_humid'] & self.burning_neighbors['several'], 
                     self.fire_prob['medium']),
            ctrl.Rule(self.wind_speed['moderate'] & self.humidity['very_humid'] & self.burning_neighbors['many'], 
                     self.fire_prob['medium']),
            ctrl.Rule(self.wind_speed['moderate'] & self.humidity['very_humid'] & self.burning_neighbors['all'], 
                     self.fire_prob['high']),
            
            # Высокая влажность
            ctrl.Rule(self.wind_speed['moderate'] & self.humidity['humid'] & self.burning_neighbors['none'], 
                     self.fire_prob['low']),
            ctrl.Rule(self.wind_speed['moderate'] & self.humidity['humid'] & self.burning_neighbors['few'], 
                     self.fire_prob['medium']),
            ctrl.Rule(self.wind_speed['moderate'] & self.humidity['humid'] & self.burning_neighbors['several'], 
                     self.fire_prob['high']),
            ctrl.Rule(self.wind_speed['moderate'] & self.humidity['humid'] & self.burning_neighbors['many'], 
                     self.fire_prob['high']),
            ctrl.Rule(self.wind_speed['moderate'] & self.humidity['humid'] & self.burning_neighbors['all'], 
                     self.fire_prob['very_high']),
            
            # Нормальная влажность
            ctrl.Rule(self.wind_speed['moderate'] & self.humidity['normal'] & self.burning_neighbors['none'], 
                     self.fire_prob['medium']),
            ctrl.Rule(self.wind_speed['moderate'] & self.humidity['normal'] & self.burning_neighbors['few'], 
                     self.fire_prob['high']),
            ctrl.Rule(self.wind_speed['moderate'] & self.humidity['normal'] & self.burning_neighbors['several'], 
                     self.fire_prob['very_high']),
            ctrl.Rule(self.wind_speed['moderate'] & self.humidity['normal'] & self.burning_neighbors['many'], 
                     self.fire_prob['very_high']),
            ctrl.Rule(self.wind_speed['moderate'] & self.humidity['normal'] & self.burning_neighbors['all'], 
                     self.fire_prob['very_high']),
            
            # Низкая влажность
            ctrl.Rule(self.wind_speed['moderate'] & self.humidity['dry'] & self.burning_neighbors['none'], 
                     self.fire_prob['high']),
            ctrl.Rule(self.wind_speed['moderate'] & self.humidity['dry'] & self.burning_neighbors['few'], 
                     self.fire_prob['very_high']),
            ctrl.Rule(self.wind_speed['moderate'] & self.humidity['dry'] & self.burning_neighbors['several'], 
                     self.fire_prob['very_high']),
            ctrl.Rule(self.wind_speed['moderate'] & self.humidity['dry'] & self.burning_neighbors['many'], 
                     self.fire_prob['very_high']),
            ctrl.Rule(self.wind_speed['moderate'] & self.humidity['dry'] & self.burning_neighbors['all'], 
                     self.fire_prob['very_high']),
        ])
        
        # Правила для сильного ветра (15-25 м/с)
        self.rules.extend([
            # Очень высокая влажность
            ctrl.Rule(self.wind_speed['strong'] & self.humidity['very_humid'] & self.burning_neighbors['none'], 
                     self.fire_prob['low']),
            ctrl.Rule(self.wind_speed['strong'] & self.humidity['very_humid'] & self.burning_neighbors['few'], 
                     self.fire_prob['medium']),
            ctrl.Rule(self.wind_speed['strong'] & self.humidity['very_humid'] & self.burning_neighbors['several'], 
                     self.fire_prob['high']),
            ctrl.Rule(self.wind_speed['strong'] & self.humidity['very_humid'] & self.burning_neighbors['many'], 
                     self.fire_prob['high']),
            ctrl.Rule(self.wind_speed['strong'] & self.humidity['very_humid'] & self.burning_neighbors['all'], 
                     self.fire_prob['very_high']),
            
            # Высокая влажность
            ctrl.Rule(self.wind_speed['strong'] & self.humidity['humid'] & self.burning_neighbors['none'], 
                     self.fire_prob['medium']),
            ctrl.Rule(self.wind_speed['strong'] & self.humidity['humid'] & self.burning_neighbors['few'], 
                     self.fire_prob['high']),
            ctrl.Rule(self.wind_speed['strong'] & self.humidity['humid'] & self.burning_neighbors['several'], 
                     self.fire_prob['very_high']),
            ctrl.Rule(self.wind_speed['strong'] & self.humidity['humid'] & self.burning_neighbors['many'], 
                     self.fire_prob['very_high']),
            ctrl.Rule(self.wind_speed['strong'] & self.humidity['humid'] & self.burning_neighbors['all'], 
                     self.fire_prob['very_high']),
            
            # Нормальная влажность
            ctrl.Rule(self.wind_speed['strong'] & self.humidity['normal'] & self.burning_neighbors['none'], 
                     self.fire_prob['high']),
            ctrl.Rule(self.wind_speed['strong'] & self.humidity['normal'] & self.burning_neighbors['few'], 
                     self.fire_prob['very_high']),
            ctrl.Rule(self.wind_speed['strong'] & self.humidity['normal'] & self.burning_neighbors['several'], 
                     self.fire_prob['very_high']),
            ctrl.Rule(self.wind_speed['strong'] & self.humidity['normal'] & self.burning_neighbors['many'], 
                     self.fire_prob['very_high']),
            ctrl.Rule(self.wind_speed['strong'] & self.humidity['normal'] & self.burning_neighbors['all'], 
                     self.fire_prob['very_high']),
            
            # Низкая влажность
            ctrl.Rule(self.wind_speed['strong'] & self.humidity['dry'] & self.burning_neighbors['none'], 
                     self.fire_prob['very_high']),
            ctrl.Rule(self.wind_speed['strong'] & self.humidity['dry'] & self.burning_neighbors['few'], 
                     self.fire_prob['very_high']),
            ctrl.Rule(self.wind_speed['strong'] & self.humidity['dry'] & self.burning_neighbors['several'], 
                     self.fire_prob['very_high']),
            ctrl.Rule(self.wind_speed['strong'] & self.humidity['dry'] & self.burning_neighbors['many'], 
                     self.fire_prob['very_high']),
            ctrl.Rule(self.wind_speed['strong'] & self.humidity['dry'] & self.burning_neighbors['all'], 
                     self.fire_prob['very_high']),
        ])
        
        # Правила для штормового ветра (25-30 м/с)
        self.rules.extend([
            # Очень высокая влажность
            ctrl.Rule(self.wind_speed['storm'] & self.humidity['very_humid'] & self.burning_neighbors['none'], 
                     self.fire_prob['medium']),
            ctrl.Rule(self.wind_speed['storm'] & self.humidity['very_humid'] & self.burning_neighbors['few'], 
                     self.fire_prob['high']),
            ctrl.Rule(self.wind_speed['storm'] & self.humidity['very_humid'] & self.burning_neighbors['several'], 
                     self.fire_prob['very_high']),
            ctrl.Rule(self.wind_speed['storm'] & self.humidity['very_humid'] & self.burning_neighbors['many'], 
                     self.fire_prob['very_high']),
            ctrl.Rule(self.wind_speed['storm'] & self.humidity['very_humid'] & self.burning_neighbors['all'], 
                     self.fire_prob['very_high']),
            
            # Высокая влажность
            ctrl.Rule(self.wind_speed['storm'] & self.humidity['humid'] & self.burning_neighbors['none'], 
                     self.fire_prob['high']),
            ctrl.Rule(self.wind_speed['storm'] & self.humidity['humid'] & self.burning_neighbors['few'], 
                     self.fire_prob['very_high']),
            ctrl.Rule(self.wind_speed['storm'] & self.humidity['humid'] & self.burning_neighbors['several'], 
                     self.fire_prob['very_high']),
            ctrl.Rule(self.wind_speed['storm'] & self.humidity['humid'] & self.burning_neighbors['many'], 
                     self.fire_prob['very_high']),
            ctrl.Rule(self.wind_speed['storm'] & self.humidity['humid'] & self.burning_neighbors['all'], 
                     self.fire_prob['very_high']),
            
            # Нормальная влажность
            ctrl.Rule(self.wind_speed['storm'] & self.humidity['normal'] & self.burning_neighbors['none'], 
                     self.fire_prob['very_high']),
            ctrl.Rule(self.wind_speed['storm'] & self.humidity['normal'] & self.burning_neighbors['few'], 
                     self.fire_prob['very_high']),
            ctrl.Rule(self.wind_speed['storm'] & self.humidity['normal'] & self.burning_neighbors['several'], 
                     self.fire_prob['very_high']),
            ctrl.Rule(self.wind_speed['storm'] & self.humidity['normal'] & self.burning_neighbors['many'], 
                     self.fire_prob['very_high']),
            ctrl.Rule(self.wind_speed['storm'] & self.humidity['normal'] & self.burning_neighbors['all'], 
                     self.fire_prob['very_high']),
            
            # Низкая влажность
            ctrl.Rule(self.wind_speed['storm'] & self.humidity['dry'] & self.burning_neighbors['none'], 
                     self.fire_prob['very_high']),
            ctrl.Rule(self.wind_speed['storm'] & self.humidity['dry'] & self.burning_neighbors['few'], 
                     self.fire_prob['very_high']),
            ctrl.Rule(self.wind_speed['storm'] & self.humidity['dry'] & self.burning_neighbors['several'], 
                     self.fire_prob['very_high']),
            ctrl.Rule(self.wind_speed['storm'] & self.humidity['dry'] & self.burning_neighbors['many'], 
                     self.fire_prob['very_high']),
            ctrl.Rule(self.wind_speed['storm'] & self.humidity['dry'] & self.burning_neighbors['all'], 
                     self.fire_prob['very_high']),
        ])
    
    #Вычисление вероятности возгорания
    def compute_fire_probability(self, wind_speed: float, humidity: float, burning_neighbors: int) -> float:
        self.simulator.input['wind_speed'] = wind_speed
        self.simulator.input['humidity'] = humidity
        self.simulator.input['burning_neighbors'] = burning_neighbors
        
        try:
            self.simulator.compute()
            return self.simulator.output['fire_prob']
        except:
            return 0.0