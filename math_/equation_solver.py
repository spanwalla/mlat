import numpy as np
from geopy.distance import geodesic
import scipy
import sys
sys.path.append('../')
from config import ureg, EQUATIONS_COUNT, DEFAULT_RECEIVERS, MAX_ITERATIONS_COUNT


def get_qr_decomposition(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    rows_num, cols_num = matrix.shape
    Q = np.empty((rows_num, cols_num))
    R = np.empty((cols_num, cols_num))
    for j in range(cols_num):
        for i in range(rows_num):
            Q[i][j] = matrix[i][j]
        for k in range(j):
            dot: float = 0
            for i in range(rows_num):
                dot += Q[i][k] * matrix[i][j]
            R[k][j] = dot
            for i in range(rows_num):
                Q[i][j] -= R[k][j] * Q[i][k]
        norm: float = 0 
        for i in range(rows_num):
            norm += Q[i][j] * Q[i][j]
        norm = np.sqrt(norm)
        for i in range(rows_num):
            Q[i][j] /= norm
        R[j][j] = norm
    return Q, R


def get_pseudo_inverse(matrix: np.ndarray) -> np.ndarray:
    Q, R = get_qr_decomposition(matrix)
    Q_transposed = Q.T
    R_inversed = R
    sum: float
    for i in range(R.shape[0] - 1, -1, -1):
        R_inversed[i][i] = 1 / R[i][i]
        for j in range(i - 1, -1, -1):
            sum = 0
            for k in range(j + 1, i + 1):
                sum += R[j][k] * R_inversed[k][i]
            R_inversed[j][i] = -sum / R[j][j]
    return R_inversed @ Q_transposed


class EquationSolver():
    def __init__(self):
        self._init_coords = np.zeros(3)
        self._init_tdoas = np.zeros(EQUATIONS_COUNT)
        self._receivers_coords: dict[np.uint16, np.ndarray] = {}
    
    def get_distance(self, from_coords: np.ndarray, to_coords: np.ndarray) -> float:
        return np.linalg.norm(to_coords - from_coords) #евклидова норма
    
    def get_jacobian_row(self, position: np.ndarray, receiver_i: np.uint8, receiver_j: np.uint8) -> list:
        jacobian_row = [0, 0, 0]
        numerator = lambda receiver_coords, plane_coords: plane_coords - receiver_coords
        denumerator = lambda index, coords: np.linalg.norm(self._receivers_coords[index] - coords)
        #denumerator = lambda index, coords: np.sqrt(geodesic((self._receivers_coords[index][0], self._receivers_coords[index][1]), (coords[0], coords[1])).m**2 
        #                                            + (self._receivers_coords[index][2]-coords[2])**2)
        denumerator_i: float = denumerator(receiver_i, position)
        denumerator_j: float = denumerator(receiver_j, position)
        #check den-r_i_j != 0
        for col in range(3):
            jacobian_row[col] = ((numerator(position[col], self._receivers_coords[receiver_i][col])) / denumerator_i 
                - numerator(position[col], self._receivers_coords[receiver_j][col]) / denumerator_j)
        return jacobian_row
    
    def get_jacobian(self, position: np.ndarray) -> np.ndarray:
        jacobian = np.empty((EQUATIONS_COUNT, 3))
        k: np.uint8 = 0
        for i in range(DEFAULT_RECEIVERS):
            for j in range(i + 1, DEFAULT_RECEIVERS):
                jacobian[k] = self.get_jacobian_row(position, i, j)
                k += 1
        return np.array(jacobian)
    
    def solve(self, tdoas: np.ndarray) -> np.ndarray:
        speed_of_light = 1 * ureg.c
        discrepancy = np.zeros(EQUATIONS_COUNT)
        equation = lambda at, rec_i, rec_j: np.abs(np.linalg.norm(self._receivers_coords[rec_i] - at) - np.linalg.norm(self._receivers_coords[rec_j] - at)) #change name
        #equation = lambda at, rec_i, rec_j: np.abs(np.sqrt(geodesic((self._receivers_coords[rec_i][0], self._receivers_coords[rec_i][1]), (at[0], at[1])).m**2 + (self._receivers_coords[rec_i][2] - at[2])**2) 
        #                                           - np.sqrt(geodesic((self._receivers_coords[rec_j][0], self._receivers_coords[rec_j][1]), (at[0], at[1])).m**2 + (self._receivers_coords[rec_j][2] - at[2])**2))
        for iteration in range(MAX_ITERATIONS_COUNT):
            jacobian = self.get_jacobian(self._init_coords)
            k: np.uint8 = 0
            for i in range(DEFAULT_RECEIVERS):
                for j in range(i + 1, DEFAULT_RECEIVERS):
                    if(self._init_tdoas[k] < 0):
                        jacobian[k] = -jacobian[k]
                        self._init_tdoas[k] = -self._init_tdoas[k] if self._init_tdoas[k] < 0 else self._init_tdoas[k] 
                    discrepancy[k] = equation(self._init_coords, i, j) - self._init_tdoas[k] * speed_of_light.to('km/s').magnitude
                    k += 1
            #print(jacobian)
            #self._init_coords = self._init_coords + get_pseudo_inverse(jacobian) @ discrepancy
            self._init_coords = self._init_coords + np.linalg.pinv(jacobian) @ discrepancy
        self._init_tdoas = tdoas
        return self._init_coords
           