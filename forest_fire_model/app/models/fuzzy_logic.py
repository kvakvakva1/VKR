import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class FuzzyFireController:
    
    def __init__(self):
        # Входные переменные
        self.wind_speed = ctrl.Antecedent(np.arange(-31, 31, 1), 'wind_speed')
        self.humidity = ctrl.Antecedent(np.arange(0, 101, 1), 'humidity')
        self.burning_neighbors = ctrl.Antecedent(np.arange(0, 9, 1), 'burning_neighbors')
        self.temperature = ctrl.Antecedent(np.arange(-20, 51, 1), 'temperature')
        
        # Выходная переменная
        self.fire_prob = ctrl.Consequent(np.arange(0, 101, 1), 'fire_prob')
        
        # Настройка функций принадлежности
        self._setup_membership_functions()
        # Создание системы правил
        self._setup_rules()
        
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulator = ctrl.ControlSystemSimulation(self.control_system)
    
    def _setup_membership_functions(self):
        # Скорость ветра - 10 категорий
        self.wind_speed['head storm'] = fuzz.trapmf(self.wind_speed.universe, [-30, -30, -25, -22])
        self.wind_speed['head strong'] = fuzz.trapmf(self.wind_speed.universe, [-25, -22, -18, -15])
        self.wind_speed['head moderate'] = fuzz.trapmf(self.wind_speed.universe, [-18, -15, -12, -10])
        self.wind_speed['head light'] = fuzz.trapmf(self.wind_speed.universe, [-12, -10, -5, -2])

        self.wind_speed['calm'] = fuzz.trapmf(self.wind_speed.universe, [-5, -2, 2, 5])

        self.wind_speed['fair light'] = fuzz.trapmf(self.wind_speed.universe, [2, 5, 10, 12])
        self.wind_speed['fair moderate'] = fuzz.trapmf(self.wind_speed.universe, [10, 12, 15, 18])
        self.wind_speed['fair strong'] = fuzz.trapmf(self.wind_speed.universe, [15, 18, 22, 25])
        self.wind_speed['fair storm'] = fuzz.trapmf(self.wind_speed.universe, [22, 25, 30, 30])
        
        # Влажность - 4 категории
        self.humidity['humid'] = fuzz.trapmf(self.humidity.universe, [60, 70, 100, 100])
        self.humidity['normal'] = fuzz.trapmf(self.humidity.universe, [40, 50, 60, 70])
        self.humidity['dry'] = fuzz.trapmf(self.humidity.universe, [20, 30, 40, 50])
        self.humidity['very_dry'] = fuzz.trapmf(self.humidity.universe, [0, 0, 20, 30])
        
        # Горящие соседи - 5 категорий
        self.burning_neighbors['none'] = fuzz.trimf(self.burning_neighbors.universe, [0, 0, 1])
        self.burning_neighbors['few'] = fuzz.trimf(self.burning_neighbors.universe, [0, 2, 4])
        self.burning_neighbors['some'] = fuzz.trimf(self.burning_neighbors.universe, [2, 4, 6])
        self.burning_neighbors['many'] = fuzz.trimf(self.burning_neighbors.universe, [4, 6, 8])
        self.burning_neighbors['all'] = fuzz.trimf(self.burning_neighbors.universe, [6, 8, 8])
        
        # Температура - 4 категории
        self.temperature['cold'] = fuzz.trapmf(self.temperature.universe, [-20, -20, 0, 10])
        self.temperature['cool'] = fuzz.trapmf(self.temperature.universe, [5, 10, 15, 20])
        self.temperature['warm'] = fuzz.trapmf(self.temperature.universe, [15, 20, 30, 35])
        self.temperature['hot'] = fuzz.trapmf(self.temperature.universe, [30, 35, 50, 50])
        
        # Вероятность возгорания - 8 категорий (можно оставить без изменений)
        self.fire_prob['extremely_low'] = fuzz.trapmf(self.fire_prob.universe, [0, 0, 5, 15])
        self.fire_prob['very_low'] = fuzz.trapmf(self.fire_prob.universe, [5, 15, 20, 30])
        self.fire_prob['low'] = fuzz.trapmf(self.fire_prob.universe, [20, 30, 35, 45])
        self.fire_prob['medium_low'] = fuzz.trapmf(self.fire_prob.universe, [35, 45, 50, 60])
        self.fire_prob['medium'] = fuzz.trapmf(self.fire_prob.universe, [50, 60, 65, 75])
        self.fire_prob['medium_high'] = fuzz.trapmf(self.fire_prob.universe, [65, 75, 80, 90])
        self.fire_prob['high'] = fuzz.trapmf(self.fire_prob.universe, [80, 85, 90, 95])
        self.fire_prob['very_high'] = fuzz.trapmf(self.fire_prob.universe, [90, 95, 100, 100])
    
    def _setup_rules(self):
        self.rules = []
        
        # Упрощенные категории
        temp_categories = ['cold', 'cool', 'warm', 'hot']
        wind_categories = ['head light', 'head moderate', 'head strong', 'head storm', 'calm', 'fair light', 'fair moderate', 'fair strong', 'fair storm']
        humidity_categories = ['humid', 'normal', 'dry', 'very_dry']
        neighbor_categories = ['none', 'few', 'some', 'many', 'all']
        
        # Обновленный маппинг весов
        def get_fire_prob_level(temp, wind, humidity, neighbors):
            temp_weights = {'cold': 1, 'cool': 2, 'warm': 3, 'hot': 4}
            wind_weights = {'head light': -1, 'head moderate': -2, 'head strong': -3, 'head storm': -4, 'calm': 0, 'fair light': 2, 'fair moderate': 3, 'fair strong': 4, 'fair storm': 5}
            humidity_weights = {'humid': 1, 'normal': 2, 'dry': 3, 'very_dry': 4}
            neighbor_weights = {'none': 1, 'few': 2, 'some': 3, 'many': 4, 'all': 5}
            
            total_weight = (
                temp_weights[temp] * 2 + 
                wind_weights[wind] * 5 + 
                humidity_weights[humidity] * 3 + 
                neighbor_weights[neighbors] * 2
            )

            if total_weight < 10:
                return 'extremely_low'
            elif 10 <= total_weight < 15:
                return 'very_low'
            elif 15 <= total_weight < 20:
                return 'low'
            elif 20 <= total_weight < 25:
                return 'medium_low'
            elif 25 <= total_weight < 30:
                return 'medium'
            elif 30 <= total_weight < 35:
                return 'medium_high'
            elif 35 <= total_weight < 40:
                return 'high'
            else:
                return 'very_high'
        
        # Генерация правил
        for temp in temp_categories:
            for wind in wind_categories:
                for humidity in humidity_categories:
                    for neighbors in neighbor_categories:
                        level = get_fire_prob_level(temp, wind, humidity, neighbors)
                        self.rules.append(
                            ctrl.Rule(
                                self.temperature[temp] & 
                                self.wind_speed[wind] & 
                                self.humidity[humidity] & 
                                self.burning_neighbors[neighbors],
                                self.fire_prob[level]
                            )
                        )
    
    def compute_fire_probability(self, wind_speed: float, humidity: float, 
                               burning_neighbors: int, temperature: float) -> float:
        self.simulator.input['wind_speed'] = wind_speed
        self.simulator.input['humidity'] = humidity
        self.simulator.input['burning_neighbors'] = burning_neighbors
        self.simulator.input['temperature'] = temperature
        
        try:
            self.simulator.compute()
            return self.simulator.output['fire_prob']
        except:
            return 0.0