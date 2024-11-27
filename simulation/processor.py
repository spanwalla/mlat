from filters import equation_solver as es
import numpy as np


class Processor:
    def __init__(self):
        self._solver = es.EquationSolver()
        self._receivers_toa: dict[int, float] = {}
    
    def init_solver(self, receivers_coords: dict[int, np.ndarray], init: np.ndarray = np.zeros(3)):
        self._solver._init_coords = init
        tdoas = np.zeros(es.EQUATIONS_COUNT)
        self.calculate_tdoa(tdoas)
        print(tdoas)
        self._solver._init_tdoas = tdoas
        self._solver._receivers_coords = receivers_coords
        
    def add_toa(self, rec_id: int, toa: float) -> None:
        self._receivers_toa[rec_id] = toa
        
    def calculate_tdoa(self, tdoas: np.ndarray) -> None:
        k = 0
        for i in range(es.DEFAULT_RECEIVERS):
            for j in range(i + 1, es.DEFAULT_RECEIVERS):
                tdoas[k] = self._receivers_toa[i] - self._receivers_toa[j]
                k += 1
        
    def process(self) -> None:
        tdoas = np.zeros(es.EQUATIONS_COUNT)
        self.calculate_tdoa(tdoas)
        coords = self._solver.solve(tdoas)  
        print(coords)
        