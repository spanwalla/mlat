from filters import equation_solver as es
import numpy as np
from filters import mlat_estimation as me


class NoiseGenerator:
    def __init__(self):
        self.mean = 0
        self.stddev = 1e-6
        
    def generate(self):
        return np.random.normal(self.mean, self.stddev)


class Processor:
    def __init__(self):
        self._solver = es.EquationSolver()
        self._receivers_toa: dict[int, float] = {}
        self._noise = NoiseGenerator()
        self._estim = me.MlatEstimation()
        self._mlat_average: np.ndarray
        self._kalman_average: np.ndarray
        self._mlat_min: np.ndarray
        self._mlat_max: np.ndarray
        self._iteration: np.int32
        self._overstatement: np.int32
    
    def init_solver(self, receivers_coords: dict[int, np.ndarray], init: np.ndarray = np.zeros(3)):
        self._solver._init_coords = init
        tdoas = np.zeros(es.EQUATIONS_COUNT)
        self.calculate_tdoa(tdoas)
        self._solver._init_tdoas = tdoas
        self._solver._receivers_coords = receivers_coords
        
    def add_toa(self, rec_id: int, toa: float) -> None:
        self._receivers_toa[rec_id] = toa
        
    def calculate_tdoa(self, tdoas: np.ndarray) -> None:
        k: int = 0
        for i in range(es.DEFAULT_RECEIVERS):
            for j in range(i + 1, es.DEFAULT_RECEIVERS):
                tdoas[k] = abs(self._receivers_toa[i] - self._receivers_toa[j])
                k += 1
        
    def process(self) -> None:
        tdoas = np.zeros(es.EQUATIONS_COUNT)
        self.calculate_tdoa(tdoas)
        mlat_coords = self._solver.solve(tdoas) 
        print(mlat_coords) 
    #     aircraft_trajectory_estimation = self._estim.estimated_state(mlat_coords)
    #     fill_vector = lambda i: np.ndarray([aircraft_trajectory_estimation[i], aircraft_trajectory_estimation[i+3], aircraft_trajectory_estimation[i+6]]) 
    #     filter_coords = fill_vector(0)
    #     filter_speed = fill_vector(1)
    #     filter_acceleration = fill_vector(2)
        
    #     self._mlat_average = mlat_coords + self._kalman_average
    #     self._kalman_average = filter_coords + self._kalman_average
    #     if self._iteration % 100 == 0:
    #         self._overstatement = 0
    #         self._mlat_average = np.zeros(3)
    #         self._mlat_min = mlat_coords
    #         self._mlat_max = mlat_coords
    #         self._kalman_average = np.zeros(3)
    #         self._iteration = 1
    #     for i in range(3):
    #         if mlat_coords[i] < self._mlat_min[i]:
    #             self._mlat_min[i] = mlat_coords[i]
    #         elif mlat_coords[i] > self._mlat_max[i]:
    #             self._mlat_max = mlat_coords[i]
    #         if np.abs(self._mlat_average[i] - self._kalman_average[i]) > self._iteration * np.abs(self._mlat_min[i] - self._mlat_max[i]):
    #             self._overstatement += 1
    #         self._iteration += 1
        
    #     if self._overstatement > config.k_duration_overstatement:
    #         aircraft_trajectory_estimation[8] = 0
    #         aircraft_trajectory_estimation[5] = 0
    #         aircraft_trajectory_estimation[2] = 0
    #         self._estim.init_state(aircraft_trajectory_estimation)
    #         self._estim.reset()
                
    # def set_sample_rate(self, sample_rate: float):
    #     self._estim.update_state_matrix(sample_rate)
        