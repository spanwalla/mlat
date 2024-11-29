from . import kalman_filter as kf
import numpy as np
from config import k_dim_state, k_space_dim

k_covariance_dispersion = [1e4, 9000, 10, 1e4, 9000, 10, 1e4, 1e3, 10]


class MlatEstimation:
    def __init__(self):
        self._filter = kf.KalmanFilter()
        self._filter._state_covariance_matrix = self.get_covariance_matrix()
        # подумать над размерностью матрицы
        covariance_error = np.zeros([k_dim_state, k_dim_state]) 
        self._filter._error_covariance_matrix = covariance_error
        
        covariance_noise = np.identity(k_space_dim)   
        self._filter._noise_covariance_matrix = k_covariance_dispersion[4] * covariance_noise
        
        observation_matrix = np.zeros([k_space_dim, k_dim_state]) 
        observation_matrix[0][0] = 1
        observation_matrix[1][3] = 1
        observation_matrix[2][6] = 1
        self._filter._observation_matrix = observation_matrix
        self._time_delta: float | None = None
    
    def update_state_matrix(self, time_delta: float) -> None:
        state_matrix = np.identity(k_dim_state)
        for i in range(0, k_dim_state, k_space_dim):
            state_matrix[i][i+1] = time_delta
            state_matrix[i][i+2] = time_delta * time_delta * 0.5
            state_matrix[i+1][i+2] = time_delta
        self._time_delta = time_delta
        self._filter._state_transition_matrix = state_matrix  # setStateMatrix
    
    def init_state(self, initial_state: np.ndarray) -> None:
        self._filter._system_vector = initial_state
    
    def get_covariance_matrix(self) -> np.ndarray:
        covariance_state = np.zeros([k_dim_state, k_dim_state])
        for i in range(k_dim_state):
            covariance_state[i][i] = k_covariance_dispersion[i]
        return covariance_state
    
    def estimated_state(self, observation: np.ndarray) -> np.ndarray:
        self._filter.predict()
        return self._filter.correct(observation)
    
    def reset(self) -> None:
        self._filter._state_covariance_matrix = self.get_covariance_matrix()
