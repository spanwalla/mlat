import numpy as np
from config import ureg, EQUATIONS_COUNT, DEFAULT_RECEIVERS, MAX_ITERATIONS_COUNT


def get_qr_decomposition(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    rows_num, cols_num = matrix.shape
    q = np.empty((rows_num, cols_num))
    r = np.empty((cols_num, cols_num))
    for j in range(cols_num):
        for i in range(rows_num):
            q[i][j] = matrix[i][j]
        for k in range(j):
            dot: float = 0
            for i in range(rows_num):
                dot += q[i][k] * matrix[i][j]
            r[k][j] = dot
            for i in range(rows_num):
                q[i][j] -= r[k][j] * q[i][k]
        norm: float = 0
        for i in range(rows_num):
            norm += q[i][j] * q[i][j]
        norm = np.sqrt(norm)
        for i in range(rows_num):
            q[i][j] /= norm
        r[j][j] = norm
    return q, r


def get_pseudo_inverse(matrix: np.ndarray) -> np.ndarray:
    q, r = get_qr_decomposition(matrix)
    q_transposed = q.T
    r_inversed = r
    for i in range(r.shape[0] - 1, -1, -1):
        r_inversed[i][i] = 1 / r[i][i]
        for j in range(i - 1, -1, -1):
            s = 0
            for k in range(j + 1, i + 1):
                s += r[j][k] * r_inversed[k][i]
            r_inversed[j][i] = -s / r[j][j]
    return r_inversed @ q_transposed


class EquationSolver:
    def __init__(self):
        self._init_coords = np.zeros(3)
        self._init_tdoas = np.zeros(EQUATIONS_COUNT)
        self._receivers_coords: dict[int, np.ndarray] = {}

    def get_jacobian_row(self, position: np.ndarray, receiver_i: int, receiver_j: int) -> list:
        jacobian_row = [0, 0, 0]

        def numerator(receiver_coords, plane_coords):
            return plane_coords - receiver_coords

        def denumerator(index, coords):
            return np.linalg.norm(self._receivers_coords[index] - coords)

        denumerator_i: float = denumerator(receiver_i, position)
        denumerator_j: float = denumerator(receiver_j, position)

        # check den-r_i_j != 0
        for col in range(3):
            jacobian_row[col] = ((numerator(position[col], self._receivers_coords[receiver_i][col])) / denumerator_i
                                 - numerator(position[col], self._receivers_coords[receiver_j][col]) / denumerator_j)
        return jacobian_row

    def get_jacobian(self, position: np.ndarray) -> np.ndarray:
        jacobian = np.empty((EQUATIONS_COUNT, 3))
        k = 0
        for i in range(DEFAULT_RECEIVERS):
            for j in range(i + 1, DEFAULT_RECEIVERS):
                jacobian[k] = self.get_jacobian_row(position, i, j)
                k += 1
        return np.array(jacobian)

    def solve(self, tdoas: np.ndarray) -> np.ndarray:
        speed_of_light = 1 * ureg.c
        discrepancy = np.zeros(EQUATIONS_COUNT)

        def get_distance_ij(at, rec_i, rec_j):
            #print("dist i_j", self._receivers_coords[rec_i], rec_i, self._receivers_coords[rec_j], rec_j, at)
            return np.abs(np.linalg.norm(self._receivers_coords[rec_i] - at) -
                          np.linalg.norm(self._receivers_coords[rec_j] - at))
            #return (np.linalg.norm(self._receivers_coords[rec_i] - self._receivers_coords[rec_j]))

        for iteration in range(MAX_ITERATIONS_COUNT):
            jacobian = self.get_jacobian(self._init_coords)
            #print(jacobian)
            k = 0
            for i in range(DEFAULT_RECEIVERS):
                for j in range(i + 1, DEFAULT_RECEIVERS):
                    if self._init_tdoas[k] < 0:
                        jacobian[k] = -jacobian[k]
                        self._init_tdoas[k] = -self._init_tdoas[k] 
                    dist_ij = get_distance_ij(self._init_coords, i, j)
                    ij_dist = self._init_tdoas[k] * speed_of_light.to('m/s').magnitude
                    #print("ls", speed_of_light.to('km/s').magnitude)
                    discrepancy[k] = dist_ij - ij_dist
                    k += 1

            self._init_coords = self._init_coords + get_pseudo_inverse(jacobian) @ discrepancy
            #self._init_coords = self._init_coords + np.linalg.pinv(jacobian) @ discrepancy

        self._init_tdoas = tdoas
        return self._init_coords
           