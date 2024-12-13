from filters import equation_solver as es
import numpy as np
from filters import mlat_estimation as me
import config
from visualization import trajectory_plotter
# import utm


class NoiseGenerator:
    def __init__(self):
        self.mean = 0
        self.stddev = 50
        
    def generate(self):
        return np.random.normal(self.mean, self.stddev)


class Processor:
    def __init__(self):
        self._solver = es.EquationSolver()
        self._receivers_toa: dict[np.uint16, float] = {}
        self._noise = NoiseGenerator()
        self._estim = me.MlatEstimation()
        self._mlat_average: np.ndarray = np.zeros(config.k_space_dim)
        self._kalman_average: np.ndarray = np.zeros(config.k_space_dim)
        self._mlat_min: np.ndarray = np.zeros(config.k_space_dim)
        self._mlat_max: np.ndarray = np.zeros(config.k_space_dim)
        self._iteration: np.int32 = 1
        self._overstatement: np.int32 = 0
        self._plotter = trajectory_plotter.TrajectoryPlotter()
    
    def init_solver(self, receivers_coords: dict[np.uint16, np.ndarray], init: np.ndarray = np.zeros(3)):
        self._solver._init_coords = init 
        tdoas = np.zeros(es.EQUATIONS_COUNT)
        self.calculate_tdoa(tdoas)
        print(tdoas)
        self._solver._init_tdoas = tdoas
        self._solver._receivers_coords = receivers_coords
        
    def add_toa(self, id: np.uint16, toa: float) -> None:
        self._receivers_toa[id] = toa
        
    def calculate_tdoa(self, tdoas: np.ndarray) -> None:
        def get_noize(i):
            return self._receivers_toa[i] * self._noise.generate()
            
        k: np.uint16 = 0
        for i in range(es.DEFAULT_RECEIVERS):
            for j in range(i + 1, es.DEFAULT_RECEIVERS):
                tdoas[k] = self._receivers_toa[i] - self._receivers_toa[j] + get_noize(j)
                #tdoas[k] = self._receivers_toa[i] - self._receivers_toa[j]
                k += 1
        
    def process(self) -> None:
        tdoas = np.zeros(es.EQUATIONS_COUNT)
        self.calculate_tdoa(tdoas)
        mlat_coords = self._solver.solve(tdoas)
        print("mlat", mlat_coords)
        #return mlat_coords
        if(mlat_coords[2] > 0):
            self._plotter.add_point_mlat(mlat_coords[0], mlat_coords[1], mlat_coords[2]) 
    
        # standard_filter_estim = self._estim.estimated_state(mlat_coords)
        
        # def fill_vector(estimation, i):
        #     return np.array([estimation[i], estimation[i+3], estimation[i+6]])
    
        # standart_filter_coords = fill_vector(standard_filter_estim, 0)
        # print(standart_filter_coords)
        # self._plotter.add_point_kalman(standart_filter_coords[0], standart_filter_coords[1], standart_filter_coords[2])
        
        # self._mlat_average = mlat_coords + self._mlat_average
        # self._kalman_average = standart_filter_coords + self._kalman_average
        # if self._iteration % 100 == 0:
        #     self._overstatement = 0
        #     self._mlat_average = np.zeros(config.k_space_dim)
        #     self._mlat_min = mlat_coords
        #     self._mlat_max = mlat_coords
        #     self._kalman_average = np.zeros(3)
        #     self._iteration = 1
        # for i in range(config.k_space_dim):
        #     if mlat_coords[i] < self._mlat_min[i]:
        #         self._mlat_min[i] = mlat_coords[i]
        #     elif mlat_coords[i] > self._mlat_max[i]:
        #         self._mlat_max[i] = mlat_coords[i]
        #     if np.abs(self._mlat_average[i] - self._kalman_average[i]) > self._iteration * np.abs(self._mlat_min[i] - self._mlat_max[i]):
        #         self._overstatement += 1
        #     self._iteration += 1
        
        # if self._overstatement > config.k_duration_overstatement:
        #     # aircraft_trajectory_estimation[8] = 0
        #     # aircraft_trajectory_estimation[5] = 0
        #     # aircraft_trajectory_estimation[2] = 0
        #     # self._estim.init_state(aircraft_trajectory_estimation)
        #     print("reset")
        #     self._estim.reset()
                
    def set_sample_rate(self, sample_rate: float):
        self._estim.update_state_matrix(sample_rate)
        