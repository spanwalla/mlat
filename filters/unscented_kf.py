import numpy as np
from config import k_equations_count, k_receivers_count, k_space_dim, k_sample_rate, k_noise_dispersion, k_light_speed

k_observation_dim = 9
k_covariance_dispersion = [1e3, 0.1, 1e3, 1e4, 0.1, 1e3, 1e3, 0.1, 1e4] #диагональные значения матрицы ковариации

class UnscentedKF:
    __slots__ = [
        '_initial_coordinates',
        '_initial_tdoas',
        '_receivers_coordinates'
        '_state',                   # (x, y, z)
        '_observation',
        '_evolution',               # F
        '_covariance_state',        # P
        '_observation_mtx',         # H
        '_observation_error'        # R
    ]
    _receivers_coordinates = {}
    
    def get_jacobian(self, position: np.ndarray) -> np.ndarray:
        jacobian = np.empty((k_equations_count, k_observation_dim))
        k = 0
        for i in range(k_receivers_count):
            for j in range(i + 1, k_receivers_count):
                jacobian[k] = self.get_jacobian_row(position, i, j)
                k += 1
        return jacobian
    
    def set_initial_params(self, initial_coordinates: np.ndarray) -> None:
        self._initial_coordinates = initial_coordinates * 0.01
        self._evolution = np.identity(k_observation_dim)
        for i in range(0, k_observation_dim, k_space_dim):
            self._evolution[i][i+1] = k_sample_rate
            self._evolution[i][i+2] = k_sample_rate * k_sample_rate * 0.5
            self._evolution[i+1][i+2] = k_sample_rate
        
        self.set_covariance_state()
        self._observation_error = k_noise_dispersion * np.identity(k_equations_count)
        
    def set_covariance_state(self) -> None:
        self._covariance_state = np.zeros((k_observation_dim, k_observation_dim))
        for i in range(k_observation_dim):
            self._covariance_state[i][i] = k_covariance_dispersion[i]
    
    def solve(self, tdoas: np.ndarray) -> np.ndarray:
        self._initial_tdoas = tdoas
        self.update_jacobian()
        self.predict()
        self.correct()
        return self._initial_coordinates
    
    def reset(self) -> None:
        self.set_covariance_state()
    
    def get_jacobian_row(self, position: np.ndarray, rec_i: int, rec_j: int) -> np.ndarray:
        jacobian_row = np.zeros(k_observation_dim)
        
        def numerator(rec_coord: float, plane_coord: float):
            return plane_coord - rec_coord
        
        def denumerator(index, coord_param):
            coordinate_param = np.ndarray([coord_param[0], coord_param[3], coord_param[6]])
            return np.linalg.norm(self._receivers_coordinates[index] - coordinate_param)
        
        denumerator_i = denumerator(rec_i, position)
        denumerator_j = denumerator(rec_j, position)
        
        for col in range(0, k_observation_dim, k_space_dim):
            jacobian_row[col] = (numerator(position[col], self._receivers_coordinates[rec_i][col / 3])/denumerator_i
                                 - numerator(position[col], self._receivers_coordinates[rec_j][col / 3])/denumerator_j)
        return jacobian_row
    
    def update_jacobian(self) -> None:
        jacobian = self.get_jacobian(self._initial_coordinates)
        k = 0
        for i in range(k_receivers_count):
            for j in range(i+1, k_receivers_count):
                if self._initial_tdoas[k] < 0:
                    jacobian[k] = -jacobian[k]
        self._observation_mtx = jacobian
    
    def compute_discrepancy(self) -> np.ndarray:
        #discrepancy = np.zeros(k_equations_count)
        def one_more_eq(at: np.ndarray):
            x = np.ndarray([at[0], at[3], at[6]])
            tdoa = np.zeros(k_equations_count)
            k = 0
            for i in range(k_receivers_count):
                for j in range(i+1, k_receivers_count):
                    tdoa[k] = np.linalg.norm(x - self._receivers_coordinates[i]) - np.linalg.norm(x - self._receivers_coordinates[j])
                    k+=1
            return tdoa
        return one_more_eq(self._initial_coordinates) - self._initial_tdoas * k_light_speed
    
    def predict(self) -> None:
        self._initial_coordinates = self._evolution @ self._initial_coordinates
        self._covariance_state = self._evolution @ self._covariance_state @ self._evolution.T
    
    def correct(self) -> None:
        S = ((self._observation_mtx @ self._covariance_state)
             @ self._observation_mtx.T + self._observation_error)
        K = (self._covariance_state @ self._observation_mtx.T) @ np.linalg.inv(S)
        I = np.identity(k_observation_dim)
        self._initial_coordinates = self._initial_coordinates + K @ self.compute_discrepancy()
        self._covariance_state = (I - K @ self._observation_mtx) @ self._covariance_state
    